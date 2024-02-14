import fs from 'fs';
import { uploadFileToMinio } from './minioClient.js'; // We will create this next

const topics = ['topic-1', 'topic-2'];

export const subscribeToTopic = (client) => {

    client.subscribe(topic, (err) => {
        if (err) {
            console.log('Subscription error:', err);
        }
    });

    client.on('message', (topic, message) => {
        const messageString = message.toString();
        console.log(`Received message on topic ${topic}: ${messageString}`);
    });
};

export const listenForFileRequests = (client) => {
    client.subscribe('file_requests', (err) => {
        if (err) {
            console.log('Subscription error:', err);
            return;
        }
    });

    client.on('message', (topic, message) => {
        if (topic === 'file_requests') {
            const request = JSON.parse(message.toString());
            if (request.action === "generateFile") {
                const size = request.size; // Size in MB
                console.log(`Generating file of size: ${size}MB`);
                const filePath = generateFile(size);
                uploadFileToMinio(filePath).then(() => {
                    console.log(`File uploaded successfully: ${filePath}`);
                }).catch(console.error);
            }
        }
    });
};

const generateFile = (sizeInMb) => {
    const filePath = `./generatedFile_${sizeInMb}MB.txt`;
    const sizeInBytes = sizeInMb * 1024 * 1024;
    const buffer = Buffer.alloc(sizeInBytes, '0');
    fs.writeFileSync(filePath, buffer);
    return filePath;
};
