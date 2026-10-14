const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { Server } = require('socket.io');
const { io: clientIO } = require('socket.io-client');
const db = require('../../src/db');
const GameEngine = require('../../src/gameEngine');
const { SocketHandler } = require('../../src/socketHandler');
const { createTempDbPath, cleanupDb } = require('../harness');

function event(socket, name) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Timed out: ${name}`)), 3000);
    socket.once(name, data => { clearTimeout(timer); resolve(data); });
  });
}
function request(socket, name, payload = {}) {
  return socket.timeout(3000).emitWithAck(name, payload);
}
function noSecrets(value) {
  if (!value || typeof value !== 'object') return;
  for (const [key, child] of Object.entries(value)) {
    assert.ok(!/canonical|correct_answer|correctAnswer|seed|mapping|synonym|explanation|isCorrect/i.test(key), `Leaked ${key}`);
    noSecrets(child);
  }
}

describe('Option shuffling with real sockets and SQLite', () => {
  let io, server, engine, handler, path, url, sockets;
  beforeEach(async () => {
    path = createTempDbPath('option_shuffle');
    const sql = db.initDb(path);
    sql.exec(`INSERT INTO ROUNDS (id, name, weight_points, default_timer_sec, sequence_order) VALUES (1, 'Easy', 1, 15, 1);
      INSERT INTO QUESTIONS (id, round_id, question_text, question_type, options_json, correct_answer, points, timer_seconds)
      VALUES (1, 1, 'Choose c', 'MCQ', '{"A":"a","B":"b","C":"c","D":"d"}', 'C', 1, 15),
             (2, 1, 'Name c', 'IDENTIFICATION', '{}', 'c', 1, 15);
      INSERT INTO CONTESTANTS (id, pin, terminal_number, student_id, full_name, department_or_section)
      VALUES (1, '1001', 1, 'S1', 'T01', 'IT'), (2, '1002', 2, 'S2', 'T02', 'IT');`);
    engine = new GameEngine();
    server = http.createServer();
    io = new Server(server);
    handler = new SocketHandler(io, engine, db);
    sockets = [];
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    url = `http://127.0.0.1:${server.address().port}`;
  });
  afterEach(async () => {
    engine._clearTimers();
    for (const socket of sockets) socket.disconnect();
    await new Promise(resolve => io.close(resolve));
    db.closeDb();
    cleanupDb(path);
  });
  async function connect(role, pin) {
    const socket = clientIO(url, { transports: ['websocket'], forceNew: true });
    sockets.push(socket);
    await event(socket, 'connect');
    const response = await request(socket, role, pin ? { pin } : {});
    assert.equal(response.success, true);
    return { socket, response };
  }
  async function stage() {
    const a = await connect('contestant:auth', '1001');
    const b = await connect('contestant:join', '1002');
    const pa = event(a.socket, 'game:phase:change');
    const pb = event(b.socket, 'game:phase:change');
    engine.stageQuestion(db.getQuestion(1));
    a.options = (await pa).state.currentQuestion.options;
    b.options = (await pb).state.currentQuestion.options;
    a.letter = Object.keys(a.options).find(k => a.options[k] === 'c');
    b.letter = Object.keys(b.options).find(k => b.options[k] === 'c');
    engine.startCountdown();
    return { a, b };
  }
  it('personalizes assignments, defeats fixture peeking, persists canonical answers and aligns reveal', async () => {
    const projector = await connect('projector:join');
    const qm = await connect('qm:join');
    const projected = event(projector.socket, 'game:phase:change');
    const managed = event(qm.socket, 'game:phase:change');
    const { a, b } = await stage();
    assert.notDeepEqual(a.options, b.options);
    assert.notEqual(a.letter, b.letter);
    assert.deepEqual((await projected).state.currentQuestion.options, db.getQuestion(1).options);
    assert.deepEqual((await managed).state.currentQuestion.options, db.getQuestion(1).options);
    const ack = await request(a.socket, 'contestant:submit', { questionId: 1, answer: a.letter.toLowerCase() });
    assert.equal(ack.success, true);
    noSecrets(ack);
    assert.equal(ack.pointsAwarded, null);
    assert.equal(ack.totalScore, 0);
    await request(b.socket, 'contestant:submit', { questionId: 1, answer: a.letter });
    assert.equal(db.getSubmission(1, 1).submitted_answer, 'C');
    assert.equal(db.getSubmission(1, 1).awarded_points, 1);
    assert.equal(db.getSubmission(2, 1).awarded_points, 0);
    assert.equal((await request(b.socket, 'contestant:submit', { questionId: 1, answer: b.letter })).error, 'DUPLICATE_SUBMISSION');
    const ra = event(a.socket, 'game:answer:reveal');
    const rb = event(b.socket, 'game:answer:reveal');
    const rp = event(projector.socket, 'game:answer:reveal');
    engine.lockQuestion();
    engine.revealAnswer();
    assert.equal((await rp).correctAnswer, 'C');
    const revealA = await ra, revealB = await rb;
    assert.equal(revealA.correctAnswer, a.letter);
    assert.equal(revealB.correctAnswer, b.letter);
    assert.equal(revealA.correctAnswerText, 'c');
    assert.equal(revealA.totalScore, 1);
    assert.ok(!Object.hasOwn(revealA, 'canonicalAnswer'));
  });
  it('T02 earns a point using its own displayed letter in an independent attempt', async () => {
    const { b } = await stage();
    await request(b.socket, 'contestant:submit', { questionId: 1, answer: b.letter });
    assert.equal(db.getSubmission(2, 1).submitted_answer, 'C');
    assert.equal(db.getSubmission(2, 1).awarded_points, 1);
  });
  it('reconnect and reauthentication preserve options and selected button without pre-reveal leakage', async () => {
    const { a } = await stage();
    await request(a.socket, 'contestant:submit', { questionId: 1, answer: a.letter });
    a.socket.disconnect();
    const restored = await connect('contestant:auth', '1001');
    for (const response of [restored.response, await request(restored.socket, 'contestant:auth', { pin: '1001' })]) {
      assert.deepEqual(response.gameState.currentQuestion.options, a.options);
      assert.equal(response.submissionStatus.submittedAnswer, a.letter);
      assert.equal(response.session.submittedAnswer, a.letter);
      assert.equal(response.submissionStatus.awardedPoints, null);
      assert.equal(response.contestant.totalScore, 0);
      noSecrets(response);
    }
    const paused = event(restored.socket, 'game:phase:change');
    engine.pauseCountdown();
    noSecrets(await paused);
    const resumed = event(restored.socket, 'game:phase:change');
    engine.resumeCountdown();
    assert.deepEqual((await resumed).state.currentQuestion.options, a.options);
    const locked = event(restored.socket, 'game:phase:change');
    engine.lockQuestion();
    noSecrets(await locked);
  });
  it('reconnecting after reveal restores the displayed correct letter', async () => {
    const { a } = await stage();
    engine.lockQuestion();
    engine.revealAnswer();
    const reveal = event(a.socket, 'game:answer:reveal');
    await request(a.socket, 'contestant:auth', { pin: '1001' });
    assert.equal((await reveal).correctAnswer, a.letter);
  });
  for (const config of [{ ENABLED: false }, { MODE: 'DISABLED' }]) {
    it(`disabled shuffling preserves canonical behavior: ${JSON.stringify(config)}`, async () => {
      handler.shuffleConfig = { ...handler.shuffleConfig, ...config };
      const { a } = await stage();
      assert.deepEqual(a.options, db.getQuestion(1).options);
      const ack = await request(a.socket, 'contestant:submit', { questionId: 1, answer: 'C' });
      assert.equal(ack.pointsAwarded, 1);
      assert.equal(db.getSubmission(1, 1).submitted_answer, 'C');
    });
  }
  it('identification bypasses shuffling and keeps text grading', async () => {
    engine.stageQuestion(db.getQuestion(2));
    const { socket, response } = await connect('contestant:auth', '1001');
    assert.deepEqual(response.gameState.currentQuestion.options, {});
    engine.startCountdown();
    assert.equal((await request(socket, 'contestant:submit', { questionId: 2, answer: 'c' })).pointsAwarded, 1);
    assert.equal(db.getSubmission(1, 2).submitted_answer, 'c');
  });
  it('a socket switching from quizmaster to contestant loses canonical room access', async () => {
    const { socket } = await connect('qm:join');
    await request(socket, 'contestant:auth', { pin: '1001' });
    const serverSocket = io.sockets.sockets.get(socket.id);
    assert.ok(!serverSocket.rooms.has('room:quizmaster'));
    const reading = event(socket, 'game:phase:change');
    engine.stageQuestion(db.getQuestion(1));
    noSecrets(await reading);
  });
});
