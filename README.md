# RAG_IACT

El objetivo de este proyecto educativo es tanto ayudar a estudiantes como aprender el funcionamiento de un RAG.

## Requerimientos previos

- 4 GB mínimos de VRAM disponibles
- Python 3.12 o superior

## Instalación

Ejecuta `./setup.sh`. Este comando crea el entorno virtual `.venv`, instala las dependencias de `requirements.txt` y genera `.env` a partir de `.env.example` si no existe.

## Configuración

`.env` define las variables de Hugging Face (ver `.env.example`):

- `HF_TOKEN`: token de acceso, solo necesario para modelos privados o con acceso restringido.
- `HF_HOME`: carpeta de caché de modelos. Si no se define, se usa `~/.cache/huggingface`.

`rag.py` no carga `.env` automáticamente, así que cárgalo antes de ejecutar:

```bash
set -a; source .env; set +a
```

## Uso

Activa el entorno y ejecuta el RAG:

```bash
source .venv/bin/activate
set -a; source .env; set +a
python rag.py
```

La primera ejecución convierte el PDF a Markdown (`ict2_reglamento.md`) y construye el índice vectorial (`ict2_index.pt`). Es normal que tarde, ya que es un proceso exigente. Después se abre una consola interactiva para hacer preguntas sobre el ICT2; escribe `salir` para terminar.

Las siguientes ejecuciones reutilizan los archivos generados, por lo que arrancan mucho antes.

## Estructura del proyecto

| Archivo | Descripción |
|---|---|
| `rag.py` | Código del RAG (preparación, indexación y modelo). |
| `setup.sh` | Configura el entorno en un solo comando. |
| `requirements.txt` | Dependencias del proyecto. |
| `.env.example` | Plantilla de variables de entorno. |
| `f_ict2_reglamento_boe2014.pdf` | Reglamento ICT2 original. |
| `ict2_reglamento.md` | Markdown generado a partir del PDF (primera ejecución). |
| `ict2_index.pt` | Índice vectorial generado (primera ejecución). |

## Backend

El RAG se divide en tres apartados:

1. **Preparación del Markdown**: `pymupdf4llm` convierte el PDF en Markdown.
2. **Indexación**: el Markdown se divide en fragmentos de hasta 1200 caracteres con un solapamiento de 200 y se vectorizan con `paraphrase-multilingual-MiniLM-L12-v2`.
3. **Modelo**: para cada pregunta se recuperan los 3 fragmentos más similares y se genera la respuesta con `Qwen/Qwen2.5-1.5B-Instruct`.
