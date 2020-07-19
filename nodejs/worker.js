const zmq = require('zeromq');
const EventEmitter = require('events');

class Worker extends EventEmitter {
    constructor(options, workerFn) {
        super();

        this.PPP_READY = Buffer.alloc(1, 1);
        this.PPP_HEARTBEAT = Buffer.alloc(1, 2);

        if (!workerFn) {
            throw new Error('Worker function must be supplied');
        }
        this.workerFn = workerFn;
        this.heartbeatLiveness = options.heartbeatLiveness || 5;
        this.heartbeatInterval = options.heartbeatInterval || 1000;
        this.intervalInit = options.intervalInit || 1000;
        this.intervalMax = options.intervalMax || 32000;

        this.url = options.url;
        this._initSocket();

        this.interval = this.intervalInit;
    }

    async _handleMessage(...args) {
        if (this.reconnectTimerId !== -1) {
            // a heartbeat has arrived whilst we were preparing to destroy and recreate the socket. cancel that
            clearTimeout(this.reconnectTimerId);
            this.reconnectTimerId = -1;
        }
        if (this.heartbeatTimerId === -1) {
            // for some reason we've received a heartbeat or message when the heartbeat timer wasn't set. schedule it again
            this._initHeartbeat();
        }
        if (args.length === 2 && args[1].toString('utf8') === this.PPP_HEARTBEAT.toString('utf8')) {
            this.liveness = this.heartbeatLiveness;
        }
        else if (args.length === 3) {
            const data = await this.workerFn(args[2]);
            this.worker.send([args[0], args[1], Buffer.from(data)]);
            this.liveness = this.heartbeatLiveness;
        }
        else {
            this.emit('error', new Error('Invalid message'));
        }
        this.interval = this.intervalInit;
    };

    _checkHeartbeat() {
        if (--this.liveness === 0) {
            // we haven't received a heartbeat in too long
            this.reconnectTimerId = setTimeout(this._heartbeatFailure.bind(this), this.interval);
            if (this.heartbeatTimerId) {
                clearTimeout(this.heartbeatTimerId);
                this.heartbeatTimerId = -1;
            }
        }
        else {
            this.worker.send(this.PPP_HEARTBEAT);
            this._initHeartbeat();
        }
    };

    _initSocket() {
        this.worker = zmq.socket('dealer');
        this.worker.setMaxListeners(3);
        this.worker.identity = 'ppw-' + process.pid + '' + Math.random() + '-' + Math.random();
        this.zmqConnected = false;
        this.worker.connect(this.url);
        this.worker.removeAllListeners('message');
        this.worker.on('message', this._handleMessage.bind(this));
        this.worker.monitor()
            .on('connect', () => {
                if (!this.zmqConnected) {
                    this.worker.send(this.PPP_READY);
                    this.liveness = this.heartbeatLiveness;
                    this.zmqConnected = true;
                    this._initHeartbeat();
                }
            })
            .on('disconnect', () => {
                if (this.zmqConnected) {
                    this.worker.removeAllListeners('message');
                    this.zmqConnected = false;
                    if (this.reconnectTimerId) {
                        clearTimeout(this.reconnectTimerId);
                    }
                    this.reconnectTimerId = setTimeout(this._heartbeatFailure.bind(this), this.interval);
                    if (this.heartbeatTimerId !== -1) {
                        clearTimeout(this.heartbeatTimerId);
                        this.heartbeatTimerId = -1;
                    }
                }
            });
    };

    _initHeartbeat() {
        if (this.heartbeatTimerId !== -1) {
            clearTimeout(this.heartbeatTimerId);
        }
        this.heartbeatTimerId = setTimeout(this._checkHeartbeat.bind(this), this.heartbeatInterval);
        if (this.reconnectTimerId !== -1) {
            clearTimeout(this.reconnectTimerId);
            this.reconnectTimerId = -1;
        }
    };

    _heartbeatFailure() {
        if (this.interval < this.intervalMax) {
            this.interval *= 2;
        }
        this.worker.close();
        this.worker = null;
        this._initSocket();
    };
}

module.exports = Worker;