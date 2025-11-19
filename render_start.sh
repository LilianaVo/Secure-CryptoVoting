#!/bin/bash

# 1. Salir inmediatamente si un comando falla (opcional, pero recomendado)
set -o errexit

# 2. Aplicar migraciones a la base de datos
echo "Aplicando migraciones..."
python manage.py migrate

# 3. Intentar crear el superusuario (si falla porque ya existe, no pasa nada)
# El "|| true" hace que si este comando falla, el script continue.
echo "Creando superusuario..."
python manage.py createsuperuser --noinput || true

# 4. Arrancar el servidor Gunicorn
echo "Iniciando Gunicorn..."
gunicorn voting_project.wsgi:application