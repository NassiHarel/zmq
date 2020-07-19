const zmq = require('zeromq');
const Queue = require('./queue');


const frontendPort = 9024;
const backendPort = 9023;

const queue = new Queue({ backendPort, frontendPort });
queue.on('frontend', function (message) {
    // console.log(Date.now() + ' - Proxying worker message through to frontend:', message.toString('utf8'));
})
queue.on('backend', function (message) {
    // console.log(Date.now() + ' - Proxying client message through to backend:', message.toString('utf8'));
});


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
        socket.connect(`inproc://frontend-queue`);
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
    let count = 0;
    setInterval(async () => {
        if (count === 5) {
            return;
        }
        count++;
        const content = `message: ${count}`;
        console.log(`client: send request`)
        const res = await send(content);
        // const y = res.toString('utf-8');
        console.log(`client: got request`)
    }, 1000)
};

main();