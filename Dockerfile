FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

CMD ["sh", "-c", "./entrypoint.sh && python manage.py runserver 0.0.0.0:8000"]
