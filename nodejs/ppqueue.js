const Queue = require('./queue');
const ppq = new Queue({ backendUrl: 'tcp://127.0.0.1:9001', frontendUrl: 'tcp://127.0.0.1:9000' });
ppq.on('frontend', function (message) {
    console.log(Date.now() + ' - Proxying worker message through to frontend:', message.toString('utf8'));
})
ppq.on('backend', function (message) {
    console.log(Date.now() + ' - Proxying client message through to backend:', message.toString('utf8'));
});
