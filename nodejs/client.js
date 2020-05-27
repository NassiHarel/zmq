
const now = require('performance-now');
const { Request } = require('./zmq-client');


class DataRequest {
    constructor({ address, content, timedOut = 600 }) {
        this.invoke = this._wrapper(this.invoke.bind(this))
        const requestAdapter = new Request({ address, content, timedOut });
        this._requestAdapter = requestAdapter;
        this._reply = new Promise((resolve) => {
            this._requestAdapter.on('message', (reply) => {
                resolve(reply);
            });
            this._requestAdapter.on('error', (error) => {
                resolve(error);
            });
            setTimeout(() => {
                if (!this._requestAdapter.isConnected()) {
                    resolve('Error Timeout');
                }
            }, timedOut);
        });
    }

    _wrapper(func) {
        const wrapper = async (args) => {
            const start = now();
            const result = await func(args);
            const end = now();
            const diff = (end - start).toFixed(3);
            const operation = func.name.replace('bound ', '');
            console.log(`${operation} - Execution time ${diff} ms`);
            return result;
        };
        return wrapper;
    }

    async invoke() {
        await this._requestAdapter.invoke();
        const rep = await this._reply;
        return rep;
    }

    close() {
        this._requestAdapter.close();
    }
}


const main = async () => {
    for (let i = 0; i < 1500; i++) {
        const request = new DataRequest({ address: { host: '127.0.0.1', port: 9020 }, content: 'hello' });
        const res = await request.invoke();
        console.log(`client: send request ${i}`)
    }
};

main();
