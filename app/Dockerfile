FROM python:3.11.8
WORKDIR /test_app
RUN pip install fastapi uvicorn redis numpy pydantic psycopg2 python-multipart
COPY src/ .
ENV PORT=5050
EXPOSE $PORT
# ENV PYTHONPATH="/test_app"
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
