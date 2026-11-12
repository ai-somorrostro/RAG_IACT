import os
import re
import torch
import pymupdf4llm
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "f_ict2_reglamento_boe2014.pdf")
MD_PATH = os.path.join(BASE_DIR, "ict2_reglamento.md")
CACHE_PATH = os.path.join(BASE_DIR, "ict2_index.pt")

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def pdf_a_markdown(pdf_path: str, md_path: str) -> str:
    if os.path.exists(md_path):
        print(f"Cargando Markdown existente desde '{md_path}'...")
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()

    print(f"Convirtiendo '{pdf_path}' a Markdown...")
    md_text = pymupdf4llm.to_markdown(pdf_path)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    return md_text


def dividir_markdown(texto_md: str, max_chars: int = 1200, overlap: int = 200) -> list[str]:
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
    if os.path.exists(CACHE_PATH):
        print("Cargando índice vectorial desde caché...")
        datos = torch.load(CACHE_PATH, map_location="cpu", weights_only=False)
        return datos["chunks"], datos["embeddings"].cpu()

    texto_md = pdf_a_markdown(PDF_PATH, MD_PATH)
    chunks = dividir_markdown(texto_md)
    print(f"Vectorizando {len(chunks)} fragmentos...")
    embeddings = embedder.encode(chunks, convert_to_tensor=True, show_progress_bar=True).cpu()

    torch.save({"chunks": chunks, "embeddings": embeddings}, CACHE_PATH)
    return chunks, embeddings


def recuperar_contexto(pregunta: str, embedder: SentenceTransformer, chunks: list[str], embeddings, top_k: int = 3) -> str:
    query_emb = embedder.encode([str(pregunta)], convert_to_tensor=True).cpu()
    resultados = util.semantic_search(query_emb, embeddings, top_k=top_k)[0]

    fragmentos = []
    for hit in resultados:
        idx = hit["corpus_id"]
        score = hit["score"]
        fragmentos.append(f"[Fragmento {idx} | Similitud: {score:.2f}]\n{chunks[idx]}")

    return "\n\n---\n\n".join(fragmentos)


def main():
    print("Inicializando modelos...")
    embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    chunks, embeddings = cargar_o_crear_indice(embedder)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"Cargando {LLM_MODEL} en {device} ({dtype})...")

    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL,
        dtype=dtype,
    ).to(device)

    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

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

        contexto = recuperar_contexto(pregunta, embedder, chunks, embeddings, top_k=3)

        mensajes = [
            {
                "role": "system",
                "content": (
                    "Eres un ingeniero experto en el Reglamento ICT2 (Real Decreto 346/2011 y Orden ITC/1644/2011). "
                    "Responde de forma precisa y concisa basándote EXCLUSIVAMENTE en el contexto proporcionado. "
                    "Si el dato no aparece en el contexto, indica que no consta en los fragmentos recuperados."
                ),
            },
            {
                "role": "user",
                "content": f"Contexto del reglamento:\n\n{contexto}\n\nPregunta: {pregunta}",
            },
        ]

        texto_entrada = tokenizer.apply_chat_template(
            mensajes,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer([texto_entrada], return_tensors="pt").to(device)

        print("\nRespuesta:")
        with torch.no_grad():
            model.generate(
                **inputs,
                max_new_tokens=350,
                do_sample=False,
                streamer=streamer,
            )


if __name__ == "__main__":
    main()