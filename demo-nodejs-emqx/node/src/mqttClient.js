import mqtt from 'mqtt';

export const createMqttClient = (clientOptions) => {
    return mqtt.connect(`mqtt://${process.env.MQTT_HOST}`, clientOptions);
};
