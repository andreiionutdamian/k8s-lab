FROM golang:1.15 as builder
RUN go get github.com/codegangsta/negroni
RUN go get github.com/gorilla/mux 
RUN go get github.com/xyproto/simpleredis/v2
COPY src/main.go .
RUN go build main.go

FROM ubuntu:18.04

COPY --from=builder /go//main /app/guestbook
ADD src/public/index.html /app/public/index.html
ADD src/public/script.js /app/public/script.js
ADD src/public/style.css /app/public/style.css
ADD src/public/jquery.min.js /app/public/jquery.min.js

WORKDIR /app
EXPOSE 3000
CMD ["./guestbook"]

