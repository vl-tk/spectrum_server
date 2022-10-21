###########
# BUILDER #
###########
FROM python:3.9-slim-bullseye

LABEL maintainer="Eugene Nitsenko <nitsenko94@gmail.com>"

RUN apt-get update -y && apt install -y netcat && apt install -y ffmpeg && apt install -y python3.9-dev && apt install -y libpango-1.0-0 && apt install -y libharfbuzz0b && apt install -y libpangoft2-1.0-0 && apt install -y libjpeg-dev && apt install -y libopenjp2-7-dev && apt install -y libffi-dev && apt install -y gcc && apt install -y wkhtmltopdf

# create the appropriate directories
ENV HOME=/usr/src/app
WORKDIR $HOME

ARG INSTALL_DEV_REQUIREMENTS="false"
# change it in production via build command
ARG DJANGO_SECRET_KEY="DJANGO_SECRET_KEY"
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    && poetry config virtualenvs.create false \
    && if [ "$INSTALL_DEV_REQUIREMENTS" == "true" ]; then \
            poetry install --no-interaction --no-ansi; \
        else \
            poetry install --only main --no-interaction --no-ansi; \
        fi

# copy project
COPY . $APP_HOME

COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH static

# URL under which media (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV MEDIA_URL /media
# Absolute path in where the media files wil be
ENV MEDIA_PATH media

RUN python manage.py collectstatic

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
