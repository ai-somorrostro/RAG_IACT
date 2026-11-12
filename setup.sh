#!/usr/bin/env bash
# Configura el entorno de RAG_IACT en un solo comando:
#   1. Crea el entorno virtual .venv (Python >= 3.12)
#   2. Instala las dependencias de requirements.txt
#   3. Crea .env a partir de .env.example si no existe
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

# Busca un Python >= 3.12; prefiere python3.12 si está disponible.
PYTHON=""
for candidate in python3.12 python3.13 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: se necesita Python >= 3.12 (encontrado: $(python3 --version 2>&1))." >&2
    exit 1
fi

echo "Usando $PYTHON ($($PYTHON --version 2>&1))"

if [ ! -d .venv ]; then
    echo "Creando entorno virtual en .venv ..."
    "$PYTHON" -m venv .venv
else
    echo ".venv ya existe; se reutiliza."
fi

echo "Instalando dependencias ..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "Creando .env a partir de .env.example ..."
    cp .env.example .env
else
    echo ".env ya existe; no se modifica."
fi

echo ""
echo "Entorno listo. Para usar el RAG:"
echo "  source .venv/bin/activate"
echo "  set -a; source .env; set +a"
echo "  python rag.py"
