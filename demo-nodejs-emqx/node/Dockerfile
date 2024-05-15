FROM node:18-alpine

COPY ./cert/HyfyRoot.crt /usr/local/share/ca-certificates/

# Update the certificate store
RUN apk update && \
    apk add --no-cache ca-certificates && \
    update-ca-certificates

WORKDIR /app

COPY . .
RUN npm install

CMD ["npm", "run", "start"]

