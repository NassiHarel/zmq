const async = require('async');
const zmq = require('zeromq');
const EventEmitter = require('events');

class Queue extends EventEmitter {
  constructor(options) {
    super();
    this.heartbeatLiveness = options.heartbeatLiveness || 5;
    this.heartbeatInterval = options.heartbeatInterval || 1000;

    this.PPP_DELIMITER = Buffer.alloc(1, 0);
    this.PPP_READY = Buffer.alloc(1, 1);
    this.PPP_HEARTBEAT = Buffer.alloc(1, 2);

    this.frontend = zmq.socket('router');   // for clients
    this.backend = zmq.socket('router');    // for workers

    this.frontend.bind(`tcp://*:${9020}`);
    this.backend.bind(options.backendUrl);

    this.workers = [];

    setInterval(this._doHeartbeat.bind(this), this.heartbeatInterval);

    this.backend.on('message', (...args) => {

      // mark worker 'identity' as ready/alive/healthy
      this._workerReady(args[0]);
      if (args[1].toString('utf8') === this.PPP_HEARTBEAT.toString('utf8') || args[1].toString('utf8') === this.PPP_READY.toString('utf8')) {
        // we've already marked this worker as ready, above; nothing more to do
      }
      else {
        const x = args[0].toString('utf8');
        const y = args[1].toString('utf8');
        const z = args[2].toString('utf8');
        var message = [args[1], this.PPP_DELIMITER, args[2]];
        this.frontend.send(message);
        this.emit('frontend', message.toString('utf8'));
      }
    });

    this.frontend.on('message', (...args) => {

      // send frontend message to next available worker
      var nextWorker = this._workerNext();
      if (!nextWorker) {
        this.emit('no workers');
      }
      else {
        // const x = args[0].toString('utf8');
        // const y = args[1].toString('utf8');
        // const z = args[1].toString('utf8');
        var message = [nextWorker.identity, args[1], args[0]];
        this.backend.send(message);
        this.emit('backend', message.toString('utf8'));
      }
    });
  }

  _workerReady(identity) {
    var found = false;
    for (var i = 0; i < this.workers.length; ++i) {
      if (this.workers[i].identity.toString('utf8') === identity.toString('utf8')) {
        // reset the timer
        clearTimeout(this.workers[i].timerId);
        this.workers[i].timerId = setTimeout(this._getPurgeWorkerTimeoutFn(identity), this.heartbeatInterval * this.heartbeatLiveness);
        found = true;
        break;
      }
    }
    if (!found) {
      this.workers.push(
        {
          identity: identity,
          timerId: setTimeout(this._getPurgeWorkerTimeoutFn(identity), this.heartbeatInterval * this.heartbeatLiveness)
        });
    }
  };

  _getPurgeWorkerTimeoutFn(identity) {
    return function () {
      for (var i = 0; i < this.workers.length; ++i) {
        var worker = this.workers[i];
        if (worker.identity.toString('utf8') === identity.toString('utf8')) {
          this.workers.splice(i, 1);
        }
      }
    }.bind(this);
  };

  _workerNext() {
    var worker = this.workers.shift();
    if (worker) {
      clearTimeout(worker.timerId);
    }
    return worker;
  };

  _doHeartbeat() {
    async.each(this.workers, function (worker, cb) {
      this.backend.send([worker.identity, this.PPP_DELIMITER, this.PPP_HEARTBEAT]);
      cb();
    }.bind(this));
  };

};

module.exports = Queue;
