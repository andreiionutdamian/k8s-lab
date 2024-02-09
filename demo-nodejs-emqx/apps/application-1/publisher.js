const os = require('os');
const mqtt = require('mqtt');

// require('dotenv').config();

// console.dir(`list all environment variables: ${JSON.stringify(process.env)}`)

Object.keys(process.env).forEach((key) => {
    if (key.startsWith('EMQX')) {
        console.log(`${key}=${process.env[key]}`);
    }
});

// configuration for the MQTT client
const clientOptions = {
    clean: true,
    // username: process.env.MQTT_USER,
    // password: process.env.MQTT_PASS,
};
console.log('clientOptions:', clientOptions);

// Ensure cadence is a number and set a default value if not specified
const cadence = Number(process.env.PUBLISH_CADENCE) || 1;

// connect to the broker
const client = mqtt.connect(`mqtt://${process.env.EMQX_SERVER_SVC_SERVICE_HOST}`, clientOptions);

client.on('connect', () => {
    console.log('Connected to MQTT broker');
});

client.on('error', (error) => {
    console.log(`Connection error: ${error}`);
    client.end();
});

const publishMessages = () => {
    for (let i = 0; i < cadence; i++) {
        const randomNumber = Math.floor(Math.random() * 100);
        const message = {
            'hostname': os.hostname(),
            'randomNumber': randomNumber,
            'cadence': cadence,
        };

        console.log(`Publishing message: ${JSON.stringify(message)}`);
        client.publish('topic-1', JSON.stringify(message));
    }
};

// publish x number of message per second according to the cadence
setInterval(publishMessages, 1000);