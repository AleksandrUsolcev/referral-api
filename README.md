# Referral API

API сервиса с аутентификацией по номеру телефона и простой реферальной системой.

[**Redoc**](https://referral-api.usolcev.com/api/v1/redoc/)

[**Postman collection**](api.postman_collection)

## Структура и описание проекта

### Авторизация по номеру телефона

Авторизация в сервисе происходит по номеру телефона в формате "+79174445566".

Для начала необходимо получить 4-х значный код, отправив POST запрос с номером телефона на эндпоинт `POST /api/v1/auth/send_code/`

После того как код получен, необходимо отправить его вместе с номером телефона на эндпоинт `POST /api/v1/auth/jwt/get_by_phone/`. Так же, вместе с номером телефона и 4-х значным кодом, можно отправить существующий 6 значный реферальный код другого пользователя.

В случае если пользователь с указанным номером телефона отсутствует, он добавляется в базу. Так же после добавления в базу, пользователю присваивается его уникальный 6 значный реферальный инвайт код.

После успешной аутентификации возвращается ответ с JWT access/refresh токенами (bearer auth). В дальнейшем они понадобятся для доступа к эндпоинтам с пользователями и редактированием профиля. Так же для работы с токенами доступны стандартный эндпоинты для проверки и рефреша: `POST /api/v1/auth/jwt/verify/`, `POST /api/v1/auth/jwt/refresh/`

### Пользователи

`GET /api/v1/users/` - просмотр списка пользователей. Поле `invite_code` является личным реферальным кодом пользователя, который уникален, неизменяем и присваивается при создании пользователя. Поле `invited_by_code` - реферальный код другого пользователя, от которого получено приглашение в сервис.

Пример как выглядят реферальные коды

```
K49FJ5
93KF75
KD82DL
DK49WL
```

`GET /api/v1/users/{id}/` - информация о конкретном пользователе

`GET /api/v1/users/current_user/` - информация о текущем пользователе

На энпдоинтах с информацией о конкретном/текущем пользователе присутствует поле `invited` со списком id и телефонами пользователей, которые приняли инвайт от просматриваемого пользователя.

`PATCH /api/v1/users/current_user/` - редактирование информации о текущем пользователе. Можно задать пользователю имя, фамилию, email адрес, а так же инвайт код, по которому он получил приглашение на сервис.

### Панель администратора

Вход в админ панель стандартно осуществляется на `/admin/`, однако вместо юзернейма или телефона, для суперюзера необходимо при создании указывать email, который и используется в качестве данных для входа. В остальных случаях, при работе через интерфейс API email не является обязательным.

## Запуск проекта в docker контейнере

Клонировать репозиторий, перейти в `referral-api/docker/` и копировать [образец](/docker/example.env) файла переменного окружения

```bash
git clone https://github.com/AleksandrUsolcev/referral-api.git
cd referral-api/docker/
cp example.env .env
```

Небольшое описание содержимого файла

```bash
# данные бд, при желании меняем имя, пользователя и пароль
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

SECRET_KEY=https://djecrety.ir/ # генерируем секретный ключ
DEBUG=False # при развертывании в докере/на сервере, оставляем False

AUTH_CODE_EXPIRES_MINUTES=30 # время действия 4-х значного кода для авторизации
REFRESH_TOKEN_LIFETIME_DAYS=14 # время действия refresh токена
ACCESS_TOKEN_LIFETIME_MINUTES=600 # время действия access токена
```

При необходимости меняем наш файл переменного окружения

```bash
vi .env
```

Разворачиваем докер контейнеры

```bash
docker compose up -d
```

Создаем суперпользователя

```bash
docker compose exec web python manage.py createsuperuser
```

## Автор

[Александр Усольцев](https://github.com/AleksandrUsolcev)
