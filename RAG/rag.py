import os
import re
import torch
import pymupdf4llm
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "f_ict2_reglamento_boe2014.pdf")  # Ajusta el nombre si es distinto
MD_PATH = os.path.join(BASE_DIR, "ict2_reglamento.md")
CACHE_PATH = os.path.join(BASE_DIR, "ict2_index.pt")

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"


def pdf_a_markdown(pdf_path: str, md_path: str) -> str:
    """Convierte el PDF a Markdown preservando encabezados y tablas."""
    if os.path.exists(md_path):
        print(f"Cargando Markdown existente desde '{md_path}'...")
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()

    print(f"Convirtiendo '{pdf_path}' (200 páginas) a Markdown. Esto tardará unos segundos...")
    md_text = pymupdf4llm.to_markdown(pdf_path)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"Archivo Markdown guardado en '{md_path}'.")
    return md_text


def dividir_markdown(texto_md: str, max_chars: int = 1400, overlap: int = 250) -> list[str]:
    """Divide el Markdown en fragmentos respetando bloques de párrafos y tablas."""
    bloques = re.split(r"\n{2,}", texto_md)
    chunks = []
    actual = ""

    for bloque in bloques:
        bloque = bloque.strip()
        if not bloque:
            continue

        if len(actual) + len(bloque) + 2 <= max_chars:
            actual = f"{actual}\n\n{bloque}" if actual else bloque
        else:
            if actual:
                chunks.append(actual)
            # Si un bloque (ej. una tabla grande) supera max_chars, se trocea con solapamiento
            if len(bloque) > max_chars:
                inicio = 0
                while inicio < len(bloque):
                    chunks.append(bloque[inicio : inicio + max_chars])
                    inicio += max_chars - overlap
                actual = ""
            else:
                solape = actual[-overlap:] if len(actual) > overlap else actual
                actual = f"{solape}\n\n{bloque}".strip()

    if actual:
        chunks.append(actual)

    return chunks


def cargar_o_crear_indice(embedder: SentenceTransformer):
    """Genera o carga los vectores del documento para evitar recalcular en cada ejecución."""
    if os.path.exists(CACHE_PATH):
        print("Cargando índice vectorial desde caché...")
        datos = torch.load(CACHE_PATH, weights_only=False)
        return datos["chunks"], datos["embeddings"]

    texto_md = pdf_a_markdown(PDF_PATH, MD_PATH)
    chunks = dividir_markdown(texto_md)
    print(f"Vectorizando {len(chunks)} fragmentos del reglamento ICT2...")
    embeddings = embedder.encode(chunks, convert_to_tensor=True, show_progress_bar=True)

    torch.save({"chunks": chunks, "embeddings": embeddings}, CACHE_PATH)
    return chunks, embeddings


def recuperar_contexto(pregunta: str, embedder: SentenceTransformer, chunks: list[str], embeddings, top_k: int = 4) -> str:
    """Busca los fragmentos más similares semánticamente a la pregunta."""
    query_emb = embedder.encode(pregunta, convert_to_tensor=True)
    resultados = util.semantic_search(query_emb, embeddings, top_k=top_k)[0]

    fragmentos_relevantes = []
    for hit in resultados:
        idx = hit["corpus_id"]
        score = hit["score"]
        fragmentos_relevantes.append(f"[Fragmento {idx} | Similitud: {score:.2f}]\n{chunks[idx]}")

    return "\n\n---\n\n".join(fragmentos_relevantes)


def main():
    print("Inicializando modelos...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    chunks, embeddings = cargar_o_crear_indice(embedder)

    generator = pipeline(
        "text-generation",
        model=LLM_MODEL,
        device_map="auto",
        dtype="auto",
    )

    print("\n" + "=" * 60)
    print("RAG ICT2 (RD 346/2011) listo. Escribe 'salir' para terminar.")
    print("=" * 60)

    while True:
        pregunta = input("\nPregunta sobre ICT2 > ").strip()
        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit"}:
            print("Cerrando asistente.")
            break

        # 1. Recuperación (Retrieval)
        contexto = recuperar_contexto(pregunta, embedder, chunks, embeddings, top_k=4)

        # 2. Construcción del prompt estructurado
        mensajes = [
            {
                "role": "system",
                "content": (
                    "Eres un ingeniero experto en el Reglamento ICT2 (Real Decreto 346/2011 y Orden ITC/1644/2011). "
                    "Responde de forma precisa y técnica basándote EXCLUSIVAMENTE en el contexto proporcionado. "
                    "Si el dato no aparece en el contexto, di que no consta en los fragmentos recuperados."
                ),
            },
            {
                "role": "user",
                "content": f"Contexto del reglamento (Markdown):\n\n{contexto}\n\nPregunta: {pregunta}",
            },
        ]

        # 3. Generación (Generation)
        salida = generator(
            mensajes,
            max_new_tokens=450,
            do_sample=False,
        )
        respuesta = salida[0]["generated_text"][-1]["content"]
        print(f"\nRespuesta:\n{respuesta}")


if __name__ == "__main__":
    main()