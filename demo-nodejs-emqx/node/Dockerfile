FROM node:18-alpine

COPY ./certs/HyfyRoot.crt /usr/local/share/ca-certificates/HyfyRoot.crt
RUN cat /usr/local/share/ca-certificates/HyfyRoot.crt >> /etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY . .
RUN npm install

CMD ["npm", "run", "start"]

