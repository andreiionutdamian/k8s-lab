import { Client } from 'minio';
import fs from "fs";

const minioClient = new Client({
    endPoint: process.env.MINIO_ENDPOINT,
    port: parseInt(process.env.MINIO_PORT),
    useSSL: process.env.MINIO_USE_SSL === 'true',
    accessKey: process.env.MINIO_ACCESS_KEY,
    secretKey: process.env.MINIO_SECRET_KEY
});

export const uploadFileToMinio = async (filePath) => {
    const bucketName = 'your-bucket-name'; // Ensure this bucket exists in your MinIO server
    const fileStream = fs.createReadStream(filePath);
    const fileStat = await fs.promises.stat(filePath);
    return minioClient.putObject(bucketName, filePath.split('/').pop(), fileStream, fileStat.size);
};
