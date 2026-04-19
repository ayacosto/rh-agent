"""
Script d'indexation des documents RH dans ChromaDB.
- Lit tous les fichiers .md dans /app/documents
- Extrait les métadonnées YAML (title, category, roles)
- Découpe le contenu en chunks
- Vectorise avec sentence-transformers
- Stocke dans ChromaDB avec filtrage par rôle
Idempotent : peut être relancé sans dupliquer les données.
"""

import os
import time
import yaml
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT  = int(os.getenv("CHROMA_PORT", 8001))
DOCUMENTS_DIR = Path("/app/documents")

CHUNK_SIZE    = 500    # caractères par chunk
CHUNK_OVERLAP = 80     # chevauchement entre chunks


# ─── Connexion ChromaDB ──────────────────────────────────
def wait_for_chroma(retries=15, delay=5):
    for i in range(retries):
        try:
            client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            client.heartbeat()
            print("ChromaDB est prêt.")
            return client
        except Exception:
            print(f"Attente ChromaDB... ({i+1}/{retries})")
            time.sleep(delay)
    raise RuntimeError("ChromaDB inaccessible après plusieurs tentatives.")


# ─── Parsing des documents Markdown ─────────────────────
def parse_markdown(filepath: Path) -> dict:
    """
    Lit un fichier .md et extrait :
    - Les métadonnées YAML du front matter (entre ---)
    - Le contenu textuel du document
    """
    content = filepath.read_text(encoding="utf-8")
    metadata = {
        "title": filepath.stem,
        "category": "general",
        "roles": ["employee"]
    }
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1])
                if meta:
                    metadata["title"]    = meta.get("title", filepath.stem)
                    metadata["category"] = meta.get("category", "general")
                    metadata["roles"]    = meta.get("roles", ["employee"])
                body = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"Erreur YAML dans {filepath.name} : {e}")

    return {"metadata": metadata, "body": body}


# ─── Chunking ────────────────────────────────────────────
def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Découpe le texte en chunks en respectant les sauts de paragraphe.
    Priorité : couper sur double saut de ligne (\n\n), puis sur \n, puis sur espace.
    """
    paragraphs = text.split("\n\n")
    chunks     = []
    current    = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) <= chunk_size:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current.strip())
            # Si le paragraphe seul dépasse chunk_size, le découper par lignes
            if len(para) > chunk_size:
                lines = para.split("\n")
                sub   = ""
                for line in lines:
                    if len(sub) + len(line) <= chunk_size:
                        sub += ("\n" if sub else "") + line
                    else:
                        if sub:
                            chunks.append(sub.strip())
                        sub = line
                if sub:
                    current = sub
                else:
                    current = ""
            else:
                current = para

    if current:
        chunks.append(current.strip())

    # Appliquer le chevauchement
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail   = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + "\n" + chunks[i])
        return overlapped

    return chunks


# ─── Indexation ──────────────────────────────────────────
def ingest_documents():
    print("=" * 50)
    print("  Démarrage de l'indexation des documents RH")
    print("=" * 50)

    # Connexion
    client     = wait_for_chroma()
    collection = client.get_or_create_collection(
        name="rh_documents",
        metadata={"hnsw:space": "cosine"}
    )

    # Modèle d'embeddings
    print("Chargement du modèle d'embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Modèle chargé.")

    # Récupérer les IDs déjà indexés pour éviter les doublons
    existing = collection.get(include=[])
    existing_ids = set(existing["ids"]) if existing["ids"] else set()
    print(f"{len(existing_ids)} chunks déjà présents dans ChromaDB.")

    # Parcourir les documents
    md_files = list(DOCUMENTS_DIR.glob("*.md"))
    if not md_files:
        print(f"Aucun fichier .md trouvé dans {DOCUMENTS_DIR}")
        return

    total_docs   = 0
    total_chunks = 0
    new_chunks   = 0

    for filepath in md_files:
        print(f"\nTraitement : {filepath.name}")
        parsed   = parse_markdown(filepath)
        metadata = parsed["metadata"]
        body     = parsed["body"]
        chunks   = split_into_chunks(body)

        print(f"  → {len(chunks)} chunks extraits")
        print(f"  → Rôles autorisés : {metadata['roles']}")

        documents  = []
        embeddings = []
        metadatas  = []
        ids        = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filepath.stem}_chunk_{i}"

            if chunk_id in existing_ids:
                continue  # Déjà indexé, on passe

            embedding = model.encode(chunk).tolist()

            # ChromaDB ne supporte pas les listes dans les métadonnées
            # On stocke le rôle le plus permissif pour le filtrage
            # Stratégie : on indexe N fois le chunk (un par rôle autorisé)
            for role in metadata["roles"]:
                role_chunk_id = f"{chunk_id}_{role}"
                if role_chunk_id not in existing_ids:
                    documents.append(chunk)
                    embeddings.append(embedding)
                    metadatas.append({
                        "title":    metadata["title"],
                        "category": metadata["category"],
                        "role":     role,
                        "source":   filepath.name,
                        "chunk_index": i
                    })
                    ids.append(role_chunk_id)
                    new_chunks += 1

        if documents:
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"  → {len(documents)} nouveaux chunks indexés")

        total_docs   += 1
        total_chunks += len(chunks)

    print("\n" + "=" * 50)
    print(f"  Indexation terminée !")
    print(f"  Documents traités : {total_docs}")
    print(f"  Total chunks      : {total_chunks}")
    print(f"  Nouveaux chunks   : {new_chunks}")
    print("=" * 50)


if __name__ == "__main__":
    ingest_documents()