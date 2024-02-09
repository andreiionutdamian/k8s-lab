const mqtt = require('mqtt');

// console.log(`list all environment variables: ${JSON.stringify(process.env)}`);
// require('dotenv').config();

Object.keys(process.env).forEach((key) => {
    if (key.startsWith('EMQX')) {
        console.log(`${key}=${process.env[key]}`);
    }
});

// configuration for the MQTT client
const clientOptions = {
    clientId: '',
    clean: true,
    // username: process.env.MQTT_USER,
    // password: process.env.MQTT_PASS,
};

// connect to the broker
const client = mqtt.connect(`mqtt://${process.env.EMQX_SERVER_SVC_SERVICE_HOST}`, clientOptions);

client.on('connect', () => {
    console.log('Connected to MQTT broker');
    client.subscribe('topic-1', (err) => {
        if (err) {
            console.log('Subscription error:', err);
        }
    });
});

client.on('error', (error) => {
    console.log(`Connection error: ${error}`);
});

client.on('message', (topic, message) => {
    const messageString = message.toString();
    console.log(`Received message on topic ${topic}: ${messageString}`);
});