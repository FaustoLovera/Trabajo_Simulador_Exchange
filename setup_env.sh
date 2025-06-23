#!/bin/bash

# setup_env.sh
# Script para configurar automáticamente el entorno de seguridad del proyecto.
# 1. Genera una clave secreta de Flask.
# 2. Crea el archivo .env con la clave.
# 3. Asegura que .env esté en .gitignore.

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

echo -e "${YELLOW}--- Iniciando configuración de entorno de seguridad ---${NC}"

# --- PASO 1: CREAR EL ARCHIVO .env CON UNA CLAVE SECRETA ---

# Nombre del archivo de entorno
ENV_FILE=".env"

# Comprobar si el archivo .env ya existe
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✅ El archivo '$ENV_FILE' ya existe. No se realizarán cambios.${NC}"
else
    echo "🔎 Generando una nueva clave secreta para Flask..."
    
    # Comprobar si python3 está disponible
    if ! command -v python3 &> /dev/null
    then
        echo -e "${YELLOW}⚠️ Advertencia: 'python3' no se encontró. Usando un generador de respaldo menos seguro.${NC}"
        # Fallback si python no está disponible, menos seguro pero funcional
        SECRET_KEY=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 48)
    else
        # Usar el módulo 'secrets' de Python para una clave criptográficamente segura
        SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(24))')
    fi

    echo "🔑 Clave generada. Creando el archivo '$ENV_FILE'..."
    # Escribir la clave en el archivo .env
    echo "# Clave secreta para sesiones de Flask. ¡NO COMPARTIR!" > $ENV_FILE
    echo "FLASK_SECRET_KEY='$SECRET_KEY'" >> $ENV_FILE
    
    echo -e "${GREEN}✅ Archivo '$ENV_FILE' creado con éxito.${NC}"
fi

# --- PASO 2: ASEGURAR QUE .env ESTÉ EN .gitignore ---

GITIGNORE_FILE=".gitignore"
ENV_IGNORE_LINE=".env"

# Comprobar si el archivo .gitignore existe
if [ ! -f "$GITIGNORE_FILE" ]; then
    echo "🔎 No se encontró el archivo '$GITIGNORE_FILE'. Creándolo..."
    touch $GITIGNORE_FILE
    echo -e "${GREEN}✅ Archivo '$GITIGNORE_FILE' creado.${NC}"
fi

# Comprobar si .env ya está en .gitignore
# grep -q silencia la salida normal, y -F trata el patrón como una cadena literal
if grep -qF "$ENV_IGNORE_LINE" "$GITIGNORE_FILE"; then
    echo -e "${GREEN}✅ '$ENV_IGNORE_LINE' ya está en '$GITIGNORE_FILE'. No se necesita ninguna acción.${NC}"
else
    echo "📝 Añadiendo '$ENV_IGNORE_LINE' a '$GITIGNORE_FILE' para evitar que se suba a Git..."
    # Añadir .env en una nueva línea al final del archivo
    echo "" >> $GITIGNORE_FILE
    echo "# Variables de entorno locales" >> $GITIGNORE_FILE
    echo "$ENV_IGNORE_LINE" >> $GITIGNORE_FILE
    echo -e "${GREEN}✅ '$ENV_IGNORE_LINE' añadido a '$GITIGNORE_FILE' con éxito.${NC}"
fi

echo -e "${YELLOW}--- Configuración de entorno completada ---${NC}"