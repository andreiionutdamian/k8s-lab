FROM python:3.11-slim

WORKDIR /app

RUN pip install paho-mqtt

COPY reader.py .

CMD ["python", "reader.py"]
