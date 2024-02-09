FROM python:3.9
WORKDIR /demo-ai-app
RUN pip install numpy fastapi uvicorn redis psycopg2 pydantic
COPY src/ .
ENV PORT=4040
CMD uvicorn main:app --host 0.0.0.0 --port $PORT