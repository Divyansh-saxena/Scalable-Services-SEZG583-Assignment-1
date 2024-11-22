FROM python:3.10-slim

LABEL maintainer "divyanshsaxena.sm@gmail.com"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY Microservice_01/artifacts ./

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
