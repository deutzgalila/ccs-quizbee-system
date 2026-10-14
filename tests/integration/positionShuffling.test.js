const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { Server } = require('socket.io');
const { io: clientIO } = require('socket.io-client');
const db = require('../../src/db');
const GameEngine = require('../../src/gameEngine');
const { SocketHandler } = require('../../src/socketHandler');
const { SHUFFLE_CONFIG } = require('../../src/config');
const { createTempDbPath, cleanupDb } = require('../harness');
const canonical = ['A', 'B', 'C', 'D'];
const options = { A: 'Jake', B: 'Jane', C: 'John', D: 'Jill' };
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
    assert.ok(!/correct_answer|correctAnswer|seed|mapping|synonym|explanation/i.test(key), `Leaked ${key}`);
    noSecrets(child);
  }
}

describe('Label-preserving position shuffling with real sockets and SQLite', () => {
  let io, engine, handler, path, url, sockets;
  beforeEach(async () => {
    path = createTempDbPath('position_shuffle');
    const sql = db.initDb(path);
    sql.exec(`INSERT INTO ROUNDS (id, name, weight_points, default_timer_sec, sequence_order) VALUES (1, 'Easy', 1, 15, 1);
      INSERT INTO QUESTIONS (id, round_id, question_text, question_type, options_json, correct_answer, points, timer_seconds)
      VALUES (1, 1, 'Choose Jake', 'MCQ', '{"A":"Jake","B":"Jane","C":"John","D":"Jill"}', 'A', 1, 15),
             (2, 1, 'Name Jake', 'IDENTIFICATION', '{}', 'Jake', 1, 15);
      INSERT INTO CONTESTANTS (id, pin, terminal_number, student_id, full_name, department_or_section)
      VALUES (1, '1001', 1, 'S1', 'T01', 'IT'), (2, '1002', 2, 'S2', 'T02', 'IT');`);
    engine = new GameEngine();
    const server = http.createServer();
    io = new Server(server);
    // Fixed fixture salt produces A in slot 3 for T01, A in slot 2 and C in slot 3 for T02.
    handler = new SocketHandler(io, engine, db, { shuffleConfig: { SEED_SALT: 'position-test-59' } });
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
    const sa = await pa, sb = await pb;
    noSecrets(sa); noSecrets(sb);
    a.question = sa.state.currentQuestion;
    b.question = sb.state.currentQuestion;
    assert.deepEqual(a.question.options, options);
    assert.deepEqual(b.question.options, options);
    engine.startCountdown();
    return { a, b };
  }
  it('copying a physical slot fails while canonical submissions score and reveal directly', async () => {
    const projector = await connect('projector:join');
    const qm = await connect('qm:join');
    const projected = event(projector.socket, 'game:phase:change');
    const managed = event(qm.socket, 'game:phase:change');
    const { a, b } = await stage();
    assert.equal(a.question.display_order[2], 'A');
    assert.equal(b.question.display_order[1], 'A');
    assert.equal(b.question.display_order[2], 'C');
    for (const payload of [await projected, await managed]) {
      assert.deepEqual(payload.state.currentQuestion.options, options);
      assert.deepEqual(payload.state.currentQuestion.display_order, canonical);
    }
    const correct = await request(a.socket, 'contestant:submit', { questionId: 1, answer: a.question.display_order[2] });
    const peeked = await request(b.socket, 'contestant:submit', { questionId: 1, answer: b.question.display_order[2] });
    assert.equal(correct.pointsAwarded, 1);
    assert.equal(peeked.pointsAwarded, 0);
    assert.equal(db.getSubmission(1, 1).submitted_answer, 'A');
    assert.equal(db.getSubmission(1, 1).awarded_points, 1);
    assert.equal(db.getSubmission(2, 1).submitted_answer, 'C');
    assert.equal(db.getSubmission(2, 1).awarded_points, 0);
    assert.equal((await request(b.socket, 'contestant:submit', { questionId: 1, answer: 'A' })).error, 'DUPLICATE_SUBMISSION');
    const reveals = [a.socket, b.socket, projector.socket, qm.socket].map(socket => event(socket, 'game:answer:reveal'));
    engine.lockQuestion(); engine.revealAnswer();
    for (const reveal of await Promise.all(reveals)) assert.equal(reveal.correctAnswer, 'A');
    assert.deepEqual(engine.getState().currentQuestion.options, options);
    assert.equal(engine.getState().currentQuestion.display_order, undefined);
  });
  it('T02 independently clicks its own slot 2 and earns a point', async () => {
    const { b } = await stage();
    const answer = b.question.display_order[1];
    assert.equal(answer, 'A');
    const ack = await request(b.socket, 'contestant:submit', { questionId: 1, answer });
    assert.equal(ack.pointsAwarded, 1);
    assert.equal(db.getSubmission(2, 1).submitted_answer, 'A');
  });
  it('reconnect, reauthentication, pause and resume preserve positions and selected canonical answer', async () => {
    const { a } = await stage();
    await request(a.socket, 'contestant:submit', { questionId: 1, answer: 'A' });
    a.socket.disconnect();
    const restored = await connect('contestant:auth', '1001');
    for (const response of [restored.response, await request(restored.socket, 'contestant:auth', { pin: '1001' })]) {
      assert.deepEqual(response.gameState.currentQuestion, a.question);
      assert.equal(response.submissionStatus.submittedAnswer, 'A');
      assert.equal(response.session.submittedAnswer, 'A');
      noSecrets(response);
    }
    const paused = event(restored.socket, 'game:phase:change'); engine.pauseCountdown();
    assert.deepEqual((await paused).state.currentQuestion.display_order, a.question.display_order);
    const resumed = event(restored.socket, 'game:phase:change'); engine.resumeCountdown();
    assert.deepEqual((await resumed).state.currentQuestion.display_order, a.question.display_order);
    for (const role of ['projector:join', 'qm:join']) {
      const { response } = await connect(role);
      assert.deepEqual(response.gameState.currentQuestion.display_order, canonical);
      assert.deepEqual(response.gameState.currentQuestion.options, options);
    }
  });
  for (const config of [{ ENABLED: false }, { MODE: 'DISABLED' }]) {
    it(`disabled shuffling retains canonical order: ${JSON.stringify(config)}`, async () => {
      handler.shuffleConfig = { ...handler.shuffleConfig, ...config };
      const { a, b } = await stage();
      assert.deepEqual(a.question.display_order, canonical);
      assert.deepEqual(b.question.display_order, canonical);
      assert.equal((await request(a.socket, 'contestant:submit', { questionId: 1, answer: 'A' })).pointsAwarded, 1);
    });
  }
  it('default configuration enables position shuffling', async () => {
    handler.shuffleConfig = SHUFFLE_CONFIG;
    assert.equal(SHUFFLE_CONFIG.ENABLED, true);
    assert.equal(SHUFFLE_CONFIG.MODE, 'LABEL_PRESERVING_POSITION');
    const { a, b } = await stage();
    assert.notDeepEqual(a.question.display_order, b.question.display_order);
  });
  it('identification passes through unchanged and keeps direct text grading', async () => {
    engine.stageQuestion(db.getQuestion(2));
    const { socket, response } = await connect('contestant:auth', '1001');
    assert.deepEqual(response.gameState.currentQuestion.options, {});
    assert.equal(response.gameState.currentQuestion.display_order, undefined);
    engine.startCountdown();
    assert.equal((await request(socket, 'contestant:submit', { questionId: 2, answer: 'Jake' })).pointsAwarded, 1);
    assert.equal(db.getSubmission(1, 2).submitted_answer, 'Jake');
  });
});
