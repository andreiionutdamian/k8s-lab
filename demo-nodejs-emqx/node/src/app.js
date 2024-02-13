const mqtt = require('mqtt');
const os = require('os'); // Required only for publisher

// Configuration for the MQTT client
const clientOptions = {
    clean: true,
    // clientId is needed only for the subscriber, but it doesn't harm the publisher to have it
    clientId: '', // Optionally, make this dynamic or environment-based if necessary
};

if (process.env.MQTT_USER) {
    clientOptions.username = process.env.MQTT_USER;
}

if (process.env.MQTT_PASS) {
    clientOptions.password = process.env.MQTT_PASS;
}

// Connect to the broker
const client = mqtt.connect(`mqtt://${process.env.MQTT_HOST}`, clientOptions);

// Check the application type from environment variable with default 'publisher'
const appType = process.env.APP_TYPE || 'publisher';

client.on('connect', () => {
    console.log(`Connected to MQTT broker as: ${appType}`);
    if (appType === 'subscriber') {
        client.subscribe('topic-1', (err) => {
            if (err) {
                console.log('Subscription error:', err);
            }
        });
    }
});

client.on('error', (error) => {
    console.log(`Connection error: ${error}`);
});

if (appType === 'publisher') {
    const cadence = Number(process.env.PUBLISH_CADENCE) || 1;

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

    // Publish x number of messages per second according to the cadence
    setInterval(publishMessages, 1000);
} else if (appType === 'subscriber') {
    client.on('message', (topic, message) => {
        const messageString = message.toString();
        console.log(`Received message on topic ${topic}: ${messageString}`);
    });
}
