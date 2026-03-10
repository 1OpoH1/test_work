# Используем официальный образ Python (версию 3.12, т.к. 3.14 может быть нестабильна)
FROM python:3.12-slim

# Устанавливаем системные зависимости (для psycopg2 и других)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Указываем порт, который будет слушать приложение
EXPOSE 8000

# Команда для запуска Gunicorn (или можно использовать runserver для разработки)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "event_planner.wsgi:application"]