# Первая версия статистики

## Подготовка

Завести .env файл с KAITEN_TOKEN=<api_token>
Токен берется из профиля пользователя в кайтене.
Файл можно скопировать из .env_template

## Использование

Для актуализации данных по пользователю запустить команду внутри контейнера с проектом:
`./manage.py get_tasks --user=<kaiten_user_id>`

Просмотр статистики:
`http://localhost:8040/statistic/simple/<local_user_id>`
