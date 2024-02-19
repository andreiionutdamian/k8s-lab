FROM python:3.11-slim

WORKDIR /app

RUN pip install paho-mqtt

ADD src/reader.py .
ADD src/base.py .

CMD ["python", "reader.py"]
