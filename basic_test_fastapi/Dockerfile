FROM python:3.9
WORKDIR /test_app
RUN pip install fastapi uvicorn redis
COPY src/ .
ENV PORT=5050
EXPOSE $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
