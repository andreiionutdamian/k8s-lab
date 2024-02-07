FROM python:3.9
WORKDIR /test_app
RUN pip install fastapi uvicorn redis numpy pydantic
COPY src/ .
ENV PORT=5050
EXPOSE $PORT
# ENV PYTHONPATH="/test_app"
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
