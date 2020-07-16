const Worker = require('./worker');

function workerFn(cb) {
    console.log(Date.now() + ' - Got a request for work');
    return cb(JSON.stringify({ ppworker: 'pretending to do work' }));
}

const ppw = new Worker({ url: 'tcp://127.0.0.1:9001' }, workerFn);