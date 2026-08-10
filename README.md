# Трекер задач сотрудников (Employee Task Tracker)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-red.svg)](https://www.django-rest-framework.org/)
[![Coverage](https://img.shields.io/badge/Coverage->75%25-brightgreen.svg)]()

Серверное REST API приложение для управления задачами сотрудников, разработанное в рамках дипломной работы. Приложение обеспечивает прозрачность процессов выполнения задач, помогает равномерно распределять нагрузку и своевременно выполнять ключевые задания.

## Особенности проекта

- **Полноценный CRUD** для управления сотрудниками и задачами.
- **Гибкая система ролей**: Обычные сотрудники, Модераторы и Суперпользователи с четким разграничением прав доступа.
- **Сложная бизнес-логика**: Поддержка родительских и дочерних задач, приоритетов, статусов и дедлайнов.
- **Многоуровневая валидация**: Проверка данных на уровне модели и сериализатора (защита от циклических зависимостей, некорректных статусов и назначения создателя задачи её же исполнителем).
- **Специальные эндпоинты**:
  - **Занятые сотрудники**: Список сотрудников, отсортированный по количеству активных задач, с детализацией самих задач.
  - **Важные задачи**: Поиск задач в статусе "Создана", от которых зависят задачи в работе, с автоматическим подбором наименее загруженных кандидатов на исполнение.
- **Автодокументация**: Интерактивная документация API через Swagger UI и ReDoc.
- **Удобные команды управления**: Кастомные management-команды для быстрого развертывания и наполнения базы тестовыми данными.
- **Контейнеризация**: Полная поддержка Docker и Docker Compose для мгновенного развертывания с Nginx и PostgreSQL.

## Технологический стек

- **Язык**: Python 3.13
- **Фреймворк**: Django, Django REST Framework (DRF)
- **База данных**: PostgreSQL 17
- **Веб-сервер**: Gunicorn + Nginx
- **Управление зависимостями**: Poetry
- **Аутентификация**: JWT (SimpleJWT)
- **Документация**: `drf-yasg` (Swagger / ReDoc)
- **Тестирование**: `pytest`, `pytest-django`, `coverage`

---

## Установка и локальный запуск

### 1. Предварительные требования
Убедитесь, что на вашем компьютере установлены:
- [Python 3.13](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Poetry](https://python-poetry.org/docs/#installation)

### 2. Клонирование репозитория

```bash
git clone git@github.com:mossssolma-ui/employee_task_tracker.git
```

### 3. Установка зависимостей

```bash
poetry install
```

### 4. Настройка переменных окружения

```bash
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=ip_site,localhost,127.0.0.1

# PostgreSQL
POSTGRES_ENGINE=
POSTGRES_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

# Команда создания суперпользователя (csu)
CSU_EMAIL=
CSU_PASSWORD=

# Логин DOCKERHUB
DOCKERHUB_USERNAME=
```

## Использование:
Для запуска приложения используется docker-compose. Приложения собраны в контейнеры, конфигурация находится в файле: `docker-compose.yml`

Запустить можно через команду:

`docker-compose up -d --build`
После запуска приложения локальным способом, вы сможете получить доступ к нему по адресу http://localhost:8000/.
В процессе запуска компоуза автоматически выполнятся кастомные команды по наполнению БД:
`python manage.py csu`,
`python manage.py create_test_users`,
`python manage.py create_test_tasks`
#### У всех тестовых пользователей (кроме суперюзера) дефолтный пароль `test123`

## Структура проекта

```
employee_task_tracker/
├── .gihub/
│   └── workflows/
│       └── ci.yaml
├── config/                             # Настройки проекта
│   ├── __init__.py
│   ├── asgi.py           
│   ├── wsgi.py                     
│   ├── settings.py         
│   └── urls.py             
├── htmlcov/                            # Покрытие тестами
│   └── index.html          
├── media/                              # Для хранения media
├── static/                             # Для хранения статики
│               
├── tasks/                              # Приложение задач
│   ├── admin.py            
│   ├── apps.py            
│   ├── models.py           
│   ├── views.py            
│   ├── serializers.py      
│   ├── permissions.py      
│   ├── urls.py             
│   ├── validators.py           
│   ├── paginators.py       
│   ├── services.py                    
│   └── tests.py            
│              
├── users/                              # Приложение пользователей
│   ├── management/
│   │   └── commands
│   │       ├── create_test_users.py    # Создание пользователей
│   │       ├── create_test_tasks.py    # Создание задач
│   │       └── csu.py                  # Создание суперюзера
│   │  
│   ├── admin.py            
│   ├── apps.py            
│   ├── models.py 
│   ├── permissions.py            
│   ├── serializers.py                       
│   ├── views.py                 
│   ├── urls.py             
│   └── tests.py            
│ 
├── Dockerfile
├── docker-compose.yaml
├── docker-compose.deploy.yaml
├── .dockerignore
├── nginx.conf
├── .flake8                             # конфиг Flake8
├── .gitignore                          # конфиг Git
├── .env.template                       # Шаблон переменных окружения
├── poetry.lock
├── pyproject.toml                      # Зависимости
└── README.md
```

## Документация
* Swagger: http://localhost/swagger/
* ReDoc: http://localhost/redoc/

## Лицензия
MIT License