
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "swasthya_django.wsgi:application", "--bind", "0.0.0.0:8000"]
