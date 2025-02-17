#!/bin/bash
docker compose down
set -a
source ./.env
set +a

if [ "${ENVIRONMENT}" = "development" ]; then

    LINE="127.0.0.1 ${URL}"$'\n'"::1 ${URL}"

    if [ -f /etc/hosts ]; then
        if ! grep -q "${URL}" /etc/hosts; then
          echo "$LINE" | sudo tee -a /etc/hosts > /dev/null
        fi
    fi

    if [ -f /mnt/c/Windows/System32/drivers/etc/hosts ]; then
        if ! grep -q "${URL}" /mnt/c/Windows/System32/drivers/etc/hosts; then
          echo "$LINE" | sudo tee -a /mnt/c/Windows/System32/drivers/etc/hosts
        fi
    fi
    if [ -d $(wslpath "$(wslvar USERPROFILE)")/AppData/Local/mkcert/ ]; then
        rm -rf ~/.local/share/mkcert/*
        cp $(wslpath "$(wslvar USERPROFILE)")/AppData/Local/mkcert/* ~/.local/share/mkcert/
    fi

    if [ ! -f ./certs/server.crt ] || [ ! -f ./certs/server.key ]; then
        mkcert --cert-file ./certs/server.crt --key-file ./certs/server.key ${URL} localhost
    fi

    if [ ! -d ./src/public/pdfjslib  ]; then
        mkdir ./src/public/pdfjslib 
        curl -L https://github.com/mozilla/pdf.js/releases/download/v4.3.136/pdfjs-4.3.136-legacy-dist.zip > ./src/public/pdfjslib/release.zip
        unzip ./src/public/pdfjslib/release.zip -d ./src/public/pdfjslib/
        rm -rf ./src/public/pdfjslib/release.zip
    fi
fi

docker compose up -d --build