#!/bin/bash
# entrypoint.sh

echo "📦 Aguardando o banco de dados subir..."
while ! nc -z postgres 5432; do
  sleep 1
done

echo "🚀 Banco de dados disponível. Rodando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "✅ Migrações aplicadas. Iniciando servidor Django..."
exec "$@"
