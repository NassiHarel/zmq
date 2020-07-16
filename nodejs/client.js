const zmq = require('zeromq');

const port = 9020;
const host = "127.0.0.1";

const _wrapper = (func) => {
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

// const buffer = Buffer.alloc(1024 * 1024 * 2000)


const send = (content) => {
    return new Promise((resolve) => {
        const socket = zmq.socket('req');
        socket.monitor(1000 - 5, 0);
        socket.on('connect', () => {
            this.connected = true;
            socket.send(content);
        });
        socket.on('disconnect', (e, g) => {
            this.connected = true;
            socket.send(content);
        });
        socket.connect(`tcp://${host}:${port}`);

        socket.on('message', (...args) => {
            return resolve(args);
        });
        socket.on('error', (error) => {
            return resolve(error);
        });

    });
}


const main = async () => {
    setInterval(async () => {
        const content = 'hello';
        const res = await send(content);
        console.log(`client: send request ${res}`)
    }, 1000)
};

main();