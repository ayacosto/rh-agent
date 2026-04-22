import os
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Chargement du modèle d'embeddings (une seule fois au démarrage)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connexion ChromaDB (lazy)
chroma_client = None
collection = None

# Client Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Mapping rôle -> rôles autorisés
ROLE_ACCESS = {
    "employee": ["employee"],
    "manager":  ["employee", "manager"],
    "rh":       ["employee", "manager", "rh"]
}


def get_collection():
    global chroma_client, collection
    if collection is None:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = chroma_client.get_or_create_collection(
            name="rh_documents",
            metadata={"hnsw:space": "cosine"}
        )
    return collection


def get_relevant_chunks(question: str, user_role: str, n_results: int = 6) -> list:
    """Recherche les chunks pertinents dans ChromaDB filtrés par rôle."""
    allowed_roles = ROLE_ACCESS.get(user_role, ["employee"])

    query_embedding = embedding_model.encode(question).tolist()

    results = get_collection().query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"role": {"$in": allowed_roles}},
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results and results["documents"]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            chunks.append({
                "content": doc,
                "title": meta.get("title", "Document RH"),
                "category": meta.get("category", "general")
            })
    return chunks


def build_prompt(question: str, chunks: list, user_context: dict) -> tuple:
    """Construit le prompt complet avec contexte utilisateur et documents."""
    context_docs = "\n\n".join([
        f"[Source : {c['title']}]\n{c['content']}"
        for c in chunks
    ])

    hire_date = str(user_context.get("hire_date", "Non renseignée"))

    system_prompt = f"""Tu es un assistant RH interne professionnel et bienveillant.
Tu reponds uniquement en te basant sur les documents fournis ci-dessous.
Reponds toujours en francais, de facon claire et structuree.

Contexte de l'employe qui pose la question :
- Nom : {user_context.get('full_name', 'Employe')}
- Poste : {user_context.get('department', 'Non renseigne')}
- Type de contrat : {user_context.get('contract_type', 'CDI')}
- Date d'embauche : {hire_date}
- Role : {user_context.get('role', 'employee')}

Documents RH disponibles :
{context_docs}

Regles importantes :
1. Si la reponse n'est pas dans les documents, dis-le clairement et oriente vers rh@entreprise.fr
2. Pour les questions complexes, detaille les etapes numerotees
3. Mentionne toujours le nom du document source entre parentheses
4. Sois precis et pratique, evite le jargon inutile
5. Ne revele jamais d'informations qui depassent le role de l'employe
6. Si la question concerne une date ou un delai de paiement, consulte toujours le document Calendrier et Informations de Paie
7. Si la question concerne la periode d essai ou le type de contrat, consulte toujours le document Politique des Contrats de Travail
8. Ne dis jamais que l information n existe pas sans avoir verifie tous les documents disponibles
9. Si l information sur la periode d essai est dans les documents, donne les durees precises selon le type de contrat de l employe (CDI Employe : 2 mois renouvelable une fois, CDI Cadre : 4 mois renouvelable une fois, CDD : 1 jour par semaine)"""

    return system_prompt, question


def call_groq(system_prompt: str, question: str) -> str:
    """Appelle l'API Groq pour générer une réponse."""
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.1,
            max_tokens=1024,
            top_p=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération de la réponse : {str(e)}"


def ask(question: str, user_role: str, user_context: dict) -> dict:
    """Fonction principale : RAG complet -> réponse + sources."""
    chunks = get_relevant_chunks(question, user_role)

    if not chunks:
        return {
            "answer": "Je n'ai pas trouvé d'information sur ce sujet dans les documents RH disponibles. "
                      "Veuillez contacter directement le service RH à rh@entreprise.fr",
            "sources": []
        }

    system_prompt, question = build_prompt(question, chunks, user_context)
    answer = call_groq(system_prompt, question)

    sources = [{"title": c["title"], "category": c["category"]} for c in chunks]
    seen = set()
    unique_sources = []
    for s in sources:
        if s["title"] not in seen:
            seen.add(s["title"])
            unique_sources.append(s)

    return {
        "answer": answer,
        "sources": unique_sources
    }