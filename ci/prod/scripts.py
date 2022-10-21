"""
Обертка вокруг команд docker для работы с сервисами
"""

import os
import string
import subprocess
import sys
from pathlib import Path
from time import sleep

ENV_FILE = Path(__file__).resolve().parent.joinpath('.server.env')
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def build():
    django_secret_key = os.environ.get("DJANGO_SECRET_KEY")
    allowed_hosts = os.environ.get("ALLOWED_HOSTS")
    main_image = os.environ.get("MAIN_IMAGE")
    cmd = f'docker build ' \
          f'--build-arg DJANGO_SECRET_KEY="{django_secret_key}" ' \
          f'--build-arg ALLOWED_HOSTS="{allowed_hosts}" ' \
          f'-t "{main_image}" {PROJECT_DIR}'
    os.system(cmd)
    return


def deploy():
    build()
    stop_main_api()
    stop_main_tasks()
    stop_main_beat()
    up_postgre_rabbit_logger_redis()
    up_monitoring()
    up_main_api('true', 'true')
    up_main_admin()
    up_main_tasks()
    up_main_beat()
    return


def up_all():
    up_postgre_rabbit_logger_redis()
    up_monitoring()
    up_services()
    return


def stop_services():
    stop_main_api()
    stop_main_admin()
    stop_main_tasks()
    stop_main_beat()
    return


def up_services():
    waiting_db()
    up_main_api('true', 'true')
    up_main_admin()
    up_main_tasks()
    up_main_beat()
    return


def stop_and_up_services():
    stop_services()
    up_services()
    return


def create_network():
    NETWORK = os.environ.get("NETWORK")
    os.system(f'docker network create --internal=false --attachable "{NETWORK}"')
    return


def up_postgre_rabbit_logger_redis():
    #  POSTGRESQL
    os.system(f'docker-compose -f services/postgre.yml up -d')
    #  AMQP RABBITMQ
    os.system(f'docker-compose -f services/rabbit.yml up -d')
    # DOCKER-LOGGER
    os.system(f'docker-compose -f services/logger.yml up -d')
    # REDIS
    os.system(f'docker-compose -f services/redis.yml up -d')
    return


def stop_postgre_rabbit_logger_redis():
    #  POSTGRESQL
    os.system(f'docker-compose -f services/postgre.yml up -d')
    #  AMQP RABBITMQ
    os.system(f'docker-compose -f services/rabbit.yml up -d')
    # DOCKER-LOGGER
    os.system(f'docker-compose -f services/logger.yml up -d')
    # REDIS
    os.system(f'docker-compose -f services/redis.yml up -d')
    return


def up_monitoring():
    os.system('docker-compose -f services/monitoring.yml up -d')
    return


def pull_main():
    os.system(f'docker pull "{os.environ.get("MAIN_IMAGE")}"')
    return


def up_main_api(waiting_database: str = 'true', migrate: str = 'false'):
    set_migration_env(waiting_database, migrate)
    os.system(f'docker-compose -f services/main_api.yml up -d')
    unset_migration_env()
    return


def up_main_admin(waiting_database: str = 'true', migrate: str = 'false'):
    set_migration_env(waiting_database, migrate)
    os.system(f'docker-compose -f services/main_admin.yml up -d')
    unset_migration_env()
    return


def up_main_tasks(waiting_database: str = 'true', migrate: str = 'false'):
    set_migration_env(waiting_database, migrate)
    os.system(f'docker-compose -f services/main_tasks.yml up -d')
    unset_migration_env()
    return


def up_main_beat(waiting_database: str = 'true', migrate: str = 'false'):
    set_migration_env(waiting_database, migrate)
    os.system(f'docker-compose -f services/main_beat.yml up -d')
    unset_migration_env()
    return


def stop_main_api():
    os.system(f'docker-compose  -f services/main_api.yml up -d')
    return


def stop_main_admin():
    os.system(f'docker-compose  -f services/main_admin.yml up -d')
    return


def stop_main_tasks():
    os.system(f'docker-compose -f services/main_tasks.yml up -d')
    return


def stop_main_beat():
    os.system(f'docker-compose -f services/main_beat.yml up -d')
    return


def waiting_db():
    host = os.environ.get("DB_HOST")
    print(f"Waiting for postgres:<{host}> when it's ready...")
    health = ''
    bat_cmd = 'docker inspect --format="{{ .State.Health.Status }}" ' + f'"{os.environ.get("DB_HOST")}"'
    while health != 'healthy':
        health = subprocess.getoutput(bat_cmd)
        sleep(0.1)
    return


def set_migration_env(waiting_database: str = 'true', migrate: str = 'false'):
    os.environ.update(dict(
        WAITING_DATABASE=waiting_database,
        MIGRATE=migrate,
    ))
    return


def unset_migration_env():
    del os.environ['WAITING_DATABASE']
    del os.environ['MIGRATE']
    return


# ==================================env========================================


def create_env():
    with open(".env.template") as t:
        template = string.Template(t.read())
        final_output = template.substitute(
            DJANGO_SETTINGS_MODULE=os.environ.get("DJANGO_SETTINGS_MODULE"),
            API_DOMAIN=os.environ.get("API_DOMAIN"),
            POSTGRES_HOST=os.environ.get("POSTGRES_HOST", 'server-postgress'),
            POSTGRES_PORT=os.environ.get("POSTGRES_PORT", 5432),
            POSTGRES_USER=os.environ.get("POSTGRES_USER", 'main'),
            POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD"),
            POSTGRES_DB=os.environ.get("POSTGRES_DB", 'main'),
            RABBITMQ_DEFAULT_USER=os.environ.get("RABBITMQ_DEFAULT_USER", 'main'),
            RABBITMQ_DEFAULT_PASS=os.environ.get("RABBITMQ_DEFAULT_PASS"),
            RABBITMQ_ERLANG_COOKIE=os.environ.get("RABBITMQ_ERLANG_COOKIE"),
            GUNICORN_WORKERS_PER_NODE=os.environ.get("GUNICORN_WORKERS_PER_NODE", '10'),
            BASE_URL=os.environ.get("BASE_URL"),
            BASE_CLIENT_URL=os.environ.get("BASE_CLIENT_URL", ""),
            ALLOWED_HOSTS=os.environ.get("ALLOWED_HOSTS"),
            MAIN_IMAGE=os.environ.get("MAIN_IMAGE"),
            DJANGO_SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY"),
            SECURE_AUTH_SALT=os.environ.get("SECURE_AUTH_SALT"),
            EMAIL_HOST=os.environ.get("EMAIL_HOST"),
            EMAIL_HOST_USER=os.environ.get("EMAIL_HOST_USER"),
            EMAIL_HOST_PASSWORD=os.environ.get("EMAIL_HOST_PASSWORD"),
            EMAIL_PORT=os.environ.get("EMAIL_PORT"),
            EMAIL_FROM=os.environ.get("EMAIL_FROM"),
        )
        with open(ENV_FILE, 'w+' if ENV_FILE.exists() else 'w') as file:
            file.write(final_output)
    return


def parse_env_file(filepath) -> dict:
    env = dict()
    with open(filepath, 'r') as fh:
        for line in fh.readlines():
            if not line.startswith('#'):
                line_dict = (tuple(line.rstrip("\n").split('=', 1)))
                if len(line_dict) == 2:
                    [k, value] = line_dict
                    env[k] = value
    return env


def load_env():
    if not ENV_FILE.exists():
        raise Exception(f'\n{ENV_FILE} DOES NOT exist!!! Please create this file')
    env = parse_env_file(ENV_FILE)
    print(f'Trying to load {ENV_FILE}')
    os.environ.update(env)
    print(f'Loaded {len(env.keys())} values: OK')


def print_env():
    env = parse_env_file(ENV_FILE) or {}
    print('\nENV:')
    print('-' * 80)
    for k in sorted(env.keys()):
        print(f'{k} = {os.environ.get(k)}')
    print('-' * 80)


def print_info():
    functions = '\n'.join(sorted([k for k in globals().keys() if callable(globals()[k])]))
    print('\nAVAILABLE COMMANDS:')
    print(functions)
    print('\nEXAMPLE: python3 scripts.py deploy')


if __name__ == "__main__":
    load_env()

    args = sys.argv
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)

    if len(args) == 1:  # means no arguments (only script itself)
        print_env()
        print_info()
    else:
        globals()[args[1]](*args[2:])
