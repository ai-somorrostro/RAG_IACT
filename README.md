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
Asistente que responde preguntas sobre el **Reglamento ICT2** (RD 346/2011) a partir del PDF oficial. Funciona en tu ordenador, gratis y sin conexión una vez instalado.

> ⚠️ El modelo es pequeño y puede equivocarse. Comprueba siempre las respuestas en el reglamento.

## Requisitos

- Linux o macOS (en Windows, usa **WSL**)
- Python **3.12 o superior** (compruébalo con `python3 --version`)
- Unos 8 GB libres en disco
- Recomendado: GPU NVIDIA con 4 GB de VRAM (sin GPU funciona, pero más lento)

## Instalación (solo la primera vez)

```bash
git clone <URL-DEL-REPOSITORIO>
cd RAG_IACT
bash setup.sh
```

El PDF `f_ict2_reglamento_boe2014.pdf` tiene que estar en la carpeta del proyecto.

## Uso

```bash
cd RAG_IACT
source .venv/bin/activate
python rag.py
```

Escribe tu pregunta y pulsa **Enter**. Para salir, escribe `salir`.

La primera vez tarda varios minutos, porque descarga los modelos y prepara el PDF. Las siguientes veces arranca mucho más rápido.

Después de cada respuesta aparecen las **fuentes**: los fragmentos del reglamento que se han usado, con su similitud. Si la pregunta no tiene relación con el reglamento, el asistente avisa en lugar de inventarse una respuesta.

**Ejemplos de preguntas:** ¿Qué es el RITI? · ¿Qué debe contener el proyecto técnico de una ICT?

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `Python >= 3.12` o error al crear `.venv` | En Ubuntu: `sudo apt install python3.12 python3.12-venv`, después `rm -rf .venv` y `bash setup.sh` |
| `No module named ...` | Te falta `source .venv/bin/activate` |
| `CUDA out of memory` | Cierra otros programas que usen la GPU |
| Respuestas raras tras cambiar el PDF | `rm ict2_index.pt ict2_reglamento.md` y vuelve a ejecutar |

## Cómo funciona

1. Convierte el PDF a texto y lo divide en fragmentos.
2. Busca los 3 fragmentos más parecidos a tu pregunta (`paraphrase-multilingual-MiniLM-L12-v2`).
3. Si son relevantes, `Qwen/Qwen2.5-1.5B-Instruct` redacta la respuesta usando solo esos fragmentos.

Los modelos, el número de fragmentos y el umbral de similitud (`UMBRAL_SIMILITUD`) se cambian en `rag.py`.
