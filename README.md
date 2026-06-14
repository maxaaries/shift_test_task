## shift_test_task

Сервис бронирования переговорных комнат.

## Запуск

```bash
cp .env.example .env
```

В `.env` для локального запуска: `DB_HOST=localhost`.  
При `docker compose up` хост БД подставляется автоматически.

### Локально

```bash
poetry install
docker compose up db -d
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8899
```

### Docker

```bash
docker compose up --build
```

Или только приложение (нужен запущенный PostgreSQL с `DB_HOST=localhost` в `.env`):

```bash
docker build -t shift_test_task .
docker run --env-file .env -p 8899:8000 shift_test_task
```

Приложение: [http://localhost:8899](http://localhost:8899)  
Документация API: [http://localhost:8899/docs](http://localhost:8899/docs)

Администратор по умолчанию: `admin@example.com` / `admin`

## Примеры

```bash
# получить токен
curl -X POST http://localhost:8899/auth/login \
  -d "username=admin@example.com&password=admin"
```

```bash
TOKEN="<access_token из ответа>"

# список комнат
curl -H "Authorization: Bearer $TOKEN" http://localhost:8899/rooms

# доступность на дату
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8899/rooms/availability?date=2026-06-15"

# создать бронь
curl -X POST http://localhost:8899/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "date": "2026-06-15"}'

# список броней
curl -H "Authorization: Bearer $TOKEN" http://localhost:8899/bookings

# отменить бронь
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:8899/bookings/1
```

## Тестовое задание выполнила Александра Миних

