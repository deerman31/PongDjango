#!/bin/bash
# entrypoint.sh

# 環境変数を設定
export DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

echo "Waiting for postgres..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "PostgreSQL started"

python mysite/manage.py makemigrations accounts

# データベースマイグレーションを実行
python mysite/manage.py migrate


# ディレクトリを /app/mysite に変更
cd /app/mysite

# DJANGO_SETTINGS_MODULE 環境変数を設定
export DJANGO_SETTINGS_MODULE=mysite.settings

# # Daphne の起動
daphne -b 0.0.0.0 -p 4242 mysite.asgi:application
