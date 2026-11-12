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

Después de cada respuesta aparece un bloque `Fuentes:` con los fragmentos del reglamento que se han usado para generarla. Cada línea muestra el número de fragmento, su similitud con la pregunta (de 0 a 1) y un extracto de sus primeros caracteres. Sirve para comprobar de dónde sale cada dato y detectar si el modelo se ha inventado algo:

```
Fuentes:
  [1] Fragmento 42 (similitud 0.67): Artículo 3. Ámbito de aplicación. Este reglamento se aplica a...
  [2] Fragmento 43 (similitud 0.61): ...
```

Si ni siquiera el fragmento más parecido alcanza el umbral de similitud (`UMBRAL_SIMILITUD`), el modelo no llega a ejecutarse y aparece el mensaje *"No he encontrado información relevante en el reglamento para esa pregunta. Prueba a reformularla con términos del reglamento."*, seguido igualmente de las fuentes para que se vea por qué se ha descartado. Suele pasar con preguntas ajenas al ICT2 o formuladas con palabras muy distintas a las del reglamento.

## Personalización

Los parámetros se ajustan en la sección `CONFIGURACIÓN` al principio de `rag.py`:

| Constante | Valor por defecto | Descripción |
|---|---|---|
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Modelo con el que se vectorizan fragmentos y preguntas. Si lo cambias, borra `ict2_index.pt` para regenerar el índice. |
| `LLM_MODEL` | `Qwen/Qwen2.5-1.5B-Instruct` | Modelo que genera las respuestas. |
| `UMBRAL_SIMILITUD` | `0.3` | Similitud mínima que debe tener el mejor fragmento para responder. Subirlo hace al asistente más estricto (responde menos, pero con fragmentos más relevantes); bajarlo hace que responda más aunque los fragmentos encajen peor. |

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
3. **Modelo**: para cada pregunta se recuperan los 3 fragmentos más similares. Si el mejor no supera `UMBRAL_SIMILITUD`, se descarta la pregunta sin llamar al modelo; en caso contrario, se genera la respuesta con `Qwen/Qwen2.5-1.5B-Instruct` y se muestran los fragmentos usados como fuentes.
