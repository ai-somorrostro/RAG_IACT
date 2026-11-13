# RAG_IACT

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

Si la pregunta no trata sobre el reglamento, el asistente responde "Solo puedo responder preguntas sobre el Reglamento ICT2."

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
