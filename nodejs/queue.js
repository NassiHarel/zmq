
const zmq = require('zeromq');
const EventEmitter = require('events');

class Queue extends EventEmitter {
  constructor(options) {
    super();
    this.heartbeatLiveness = options.heartbeatLiveness || 5;
    this.heartbeatInterval = options.heartbeatInterval || 1000;
    this.queueInterval = options.queueInterval || 1000;

    this.PPP_DELIMITER = Buffer.alloc(1, 0);
    this.PPP_READY = Buffer.alloc(1, 1);
    this.PPP_HEARTBEAT = Buffer.alloc(1, 2);

    this.frontend = zmq.socket('router');   // for clients
    this.backend = zmq.socket('router');    // for workers

    this.frontend.bind(`inproc://frontend-queue`);
    this.backend.bind(`tcp://*:${options.backendPort}`);

    this.workers = [];
    this.queue = [];

    setInterval(this._doHeartbeat.bind(this), this.heartbeatInterval);
    setInterval(this._queueFlush.bind(this), this.queueInterval);

    this.backend.on('message', (...args) => {

      // mark worker 'identity' as ready/alive/healthy
      this._workerReady(args[0]);
      if (args[1].toString('utf8') === this.PPP_HEARTBEAT.toString('utf8') || args[1].toString('utf8') === this.PPP_READY.toString('utf8')) {
        // we've already marked this worker as ready, above; nothing more to do
      }
      else {
        const message = args.slice(1);
        this.frontend.send(message);
        this.emit('frontend', message.toString('utf8'));
      }
    });

    this.frontend.on('message', (...args) => {
      // send frontend message to next available worker
      const nextWorker = this._workerNext();
      if (!nextWorker) {
        this.queue.push(args);
      }
      else {
        const message = [nextWorker.identity, ...args];
        this.backend.send(message);
        this.emit('backend', message.toString('utf8'));
      }
    });
  }

  _queueFlush() {
    const nextWorker = this._workerNext();
    if (nextWorker) {
      const q = this.queue.shift();
      if (q) {
        const message = [nextWorker.identity, ...q];
        this.backend.send(message);
        console.log(`backend: send`)
      }
    }
  }

  _workerReady(identity) {
    const worker = this.workers.find(w => w.identity.toString('utf8') === identity.toString('utf8'))
    if (worker) {
      // reset the timer
      clearTimeout(worker.timerId);
      worker.timerId = setTimeout(this._getPurgeWorkerTimeoutFn(identity), this.heartbeatInterval * this.heartbeatLiveness);
    }
    else {
      this.workers.push({
        identity,
        timerId: setTimeout(this._getPurgeWorkerTimeoutFn(identity), this.heartbeatInterval * this.heartbeatLiveness)
      });
    }
  };

  _getPurgeWorkerTimeoutFn(identity) {
    return () => {
      for (let i = 0; i < this.workers.length; ++i) {
        const worker = this.workers[i];
        if (worker.identity.toString('utf8') === identity.toString('utf8')) {
          this.workers.splice(i, 1);
        }
      }
    };
  };

  _workerNext() {
    const worker = this.workers.shift();
    if (worker) {
      clearTimeout(worker.timerId);
    }
    return worker;
  }

  _doHeartbeat() {
    return Promise.all(this.workers.map(w => this.backend.send([w.identity, this.PPP_DELIMITER, this.PPP_HEARTBEAT])));
  };
}

module.exports = Queue;
