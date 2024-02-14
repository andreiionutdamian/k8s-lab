import os from 'os';

export const startPublishing = (client, cadence) => {
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

    setInterval(publishMessages, 1000);
};

export const requestFileGeneration = (client) => {
    const fileSize = (Math.random() * (20 - 10) + 10).toFixed(2); // Generates a random size between 10 to 20
    const message = {
        action: "generateFile",
        size: fileSize, // in MB
    };

    console.log(`Requesting file generation: ${JSON.stringify(message)}`);
    client.publish('file_requests', JSON.stringify(message));
};
