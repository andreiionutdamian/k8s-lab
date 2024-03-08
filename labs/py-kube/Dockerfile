FROM python:3.11-slim

WORKDIR /test_app


RUN pip install numpy kmonitor


ADD test_package.py .

CMD python test_package.py

