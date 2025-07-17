# syntax=docker/dockerfile:1

FROM python:3.12.11-slim-bullseye

WORKDIR /sql-app

EXPOSE 80

COPY requirements.txt /sql-app/

RUN apt-get update && \
    apt-get install -y wget unzip curl gnupg python3-dev build-essential libpcre3 libpcre3-dev unixodbc unixodbc-dev g++ \
    && curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN pip3 install --no-cache -r requirements.txt

RUN wget https://releases.hashicorp.com/vault/1.20.0/vault_1.20.0_linux_amd64.zip \
    && unzip -o vault_1.20.0_linux_amd64.zip -d /usr/local/bin/

COPY app.py /sql-app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
