FROM python:3.9-alpine

WORKDIR /app

# Копіюємо та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

# Запускаємо сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]