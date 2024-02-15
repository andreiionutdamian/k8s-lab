import { createMqttClient } from './mqttClient.js';
import { startPublishing, requestFileGeneration } from './publisher.js';
import { listenForFileRequests, subscribeToTopic } from './subscriber.js';

const clientOptions = {
    clean: true,
    clientId: '',
};

if (process.env.MQTT_USER) {
    clientOptions.username = process.env.MQTT_USER;
}

if (process.env.MQTT_PASS) {
    clientOptions.password = process.env.MQTT_PASS;
}

const client = createMqttClient(clientOptions);

const appType = process.env.APP_TYPE || 'publisher';

client.on('connect', () => {
    console.log(`Connected to MQTT broker as: ${appType}`);
});

client.on('error', (error) => {
    console.log(`Connection error: ${error}`);
});

if (appType === 'publisher') {
    const cadence = Number(process.env.PUBLISH_CADENCE) || 1;
    startPublishing(client, cadence);

    // set a 10-minute interval to request file generation
    setInterval(() => {
        requestFileGeneration(client);
    }, 60000);

} else if (appType === 'subscriber') {
    subscribeToTopic(client);
    listenForFileRequests(client);
}
