FROM node:9.4.0-alpine
WORKDIR /test_app
ADD src/app.js .
ADD src/package.json .
RUN npm install &&\
    apk update &&\
    apk upgrade
EXPOSE  8080
CMD node app.js
