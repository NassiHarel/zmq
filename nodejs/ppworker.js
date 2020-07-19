const Worker = require('./worker');

function workerFn(d) {
    console.log(Date.now() + ' - Got a request for work');
    const data = d.toString('utf8');
    return data + " world";
}

const ppw = new Worker({ url: 'tcp://127.0.0.1:9023' }, workerFn);