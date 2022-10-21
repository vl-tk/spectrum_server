# This is main server for Spectrum Site! #

- Django 4.1
- Postgres 14.5

## What needs to be done to run the service locally?

- [Install Docker](https://docs.docker.com/install/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

### Clone repository

```
git clone https://github.com/GoodBitDev/spectrum_server
```

## RUN WITH DOCKER

### Set up local confiuration files

```
cp main/settings/local-docker.py.example main/settings/local-docker.py
```

### Start infrastructure

```
docker-compose up -d
```

### Create a superuser for the admin panel

```
docker exec -it main bash
python manage.py createsuperuser
```

## RUN LOCALLY

### 1. Run Postgres, Redis, RabbitMQ in docker

```
docker-compose up -d postgres redis rabbit
```

### 2. Create local config files

```
cp main/settings/local.py.example main/settings/local.py
cp main/settings/local-docker.py.example main/settings/local-docker.py
```

### 3. Install poetry package manager

```
pip install poetry
poetry install  # will create virtualenv and install packages
poetry shell  # will activate virtual environment for current session
```

### 4. Run django

#### From terminal

```
# WINDOWS
set DJANGO_SETTINGS_MODULE=main.settings.local
# UNIX
export DJANGO_SETTINGS_MODULE=main.settings.local

python manage.py migrate
python manage.py createsuperuser
# then
python manage.py runserver 0.0.0.0:4096
```
#### Or run in VSCode

Check virtualenv info and python location:
```
poetry env info
```
Open this path in the list of interpreters in VSCode and select bin/python or Scripts/python.exe

launch.json with this python file should be created. Then run (green triangle button).


### 5. To run Celery workers locally
```
# WINDOWS
set DJANGO_SETTINGS_MODULE=main.settings.local
celery -A main worker -l debug

# UNIX
export DJANGO_SETTINGS_MODULE=main.settings.local
celery -A main worker -l debug
```

### 6. To run the Celery crontab locally
```
# WINDOWS
set DJANGO_SETTINGS_MODULE=main.settings.local
celery -A main beat -l debug

# UNIX
export DJANGO_SETTINGS_MODULE=main.settings.local
celery -A main beat -l debug
```

---


## CHECK TESTS CODE COVERAGE 


```
coverage run && coverage report
coverage run && coverage html
```

