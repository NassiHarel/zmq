const zmq = require('zeromq');

const port = 5555;
const host = "127.0.0.1";

const send = (content) => {
    return new Promise((resolve) => {
        const socket = zmq.socket('req');
        socket.monitor(1000 - 5, 0);
        socket.on('connect', () => {
            console.log(`connected`)
        });
        socket.on('disconnect', (e, g) => {
            console.log(`disconnected`)
        });
        socket.connect(`tcp://${host}:${port}`);
        socket.on('message', (message) => {
            return resolve(message);
        });
        socket.on('error', (error) => {
            return resolve(error);
        });
        socket.send(content);
    });
}

const main = async () => {
    setInterval(async () => {
        const content = 'hello'
        const res = await send(content);
        const sa = res.toString();
        console.log(`client: got request ${res}`)
    }, 2000)
};

main();