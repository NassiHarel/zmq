const EventEmitter = require('events');
const { Server } = require('./zmq-server');

const buffer = Buffer.alloc(1024 * 1024 * 5, 0xdd);

class DataServer extends EventEmitter {
    constructor({ host, port }) {
        super();
        this._adapter = new Server({ port });
        this._host = host;
        this._port = port;
    }

    async listen() {
        await this._adapter.listen(this._port, (m) => this._createReply(m));
        console.log(`discovery serving on ${this._host}:${this._port} with ${this._encodingType} encoding`);
    }

    _createReply(message) {
        return buffer;
    }
}

const server = new DataServer({ host: '127.0.0.1', port: 9020 });
server.listen();
