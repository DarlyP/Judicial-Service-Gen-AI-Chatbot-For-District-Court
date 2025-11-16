# FAQ LLM core workflow from CSV to FAISS with deterministic, RAG, and fallback modes
import os, json, time, hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import requests

# Optional guard that prevents Transformers from loading TensorFlow when rerankers are added later
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_JAX", "0")
os.environ.setdefault("USE_TORCH", "1")

# Configuration section that can be adjusted for deployment
APP_DATA_DIR = Path(os.getenv("APP_DATA_DIR", "/tmp/appdata"))

CSV_PATH = Path("Data/standar_layanan_combined.csv")  # CSV file must contain columns: category, question, answer
INDEX_DIR = APP_DATA_DIR / "index_store"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

EMB_MODEL = "intfloat/multilingual-e5-small"  # Multilingual lightweight embedding model
TOP_K = 20

# Thresholds for three lane routing logic
HIGH_THRESHOLD = 0.880  # High confidence path that answers directly from CSV
LOW_THRESHOLD  = 0.820  # Low confidence boundary that triggers fallback logic

# RAG configuration used when Ollama is installed and model is available
ENABLE_RAG = True
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "gemma2:9b"

LOG_PATH = APP_DATA_DIR / "query_log.jsonl"

# CSV loading and embedding utilities
def read_csv_clean(csv_path: os.PathLike | str) -> pd.DataFrame:
    """Load FAQ CSV and normalize mandatory columns, then create combined doc_text."""
    df = pd.read_csv(csv_path)
    required = {"category","question","answer"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"CSV must contain columns: {required}. Got: {df.columns.tolist()}")
    df = df.dropna(subset=["category","question","answer"]).reset_index(drop=True)
    df["category"] = df["category"].astype(str).str.strip()
    df["question"] = df["question"].astype(str).str.strip()
    df["answer"]   = df["answer"].astype(str).str.strip()
    df["doc_text"] = "[" + df["category"] + "] Q: " + df["question"] + "\nA: " + df["answer"]
    return df

def row_hash(cat: str, q: str, a: str) -> str:
    return hashlib.sha1(f"{cat}||{q}||{a}".encode("utf-8")).hexdigest()

def load_embedder(name: str = EMB_MODEL) -> SentenceTransformer:
    # Lazy singleton loader to avoid repeated model initialization
    if not hasattr(load_embedder, "_model"):
        load_embedder._model = SentenceTransformer(name)
    return load_embedder._model  # type: ignore[attr-defined]

def encode_passages(texts: List[str]) -> np.ndarray:
    # Encode FAQ passages with passage prefix and normalized embeddings
    model = load_embedder()
    return model.encode(["passage: " + t for t in texts], normalize_embeddings=True, show_progress_bar=True).astype(np.float32)

def encode_queries(queries: List[str]) -> np.ndarray:
    # Encode user queries with query prefix for asymmetric retrieval
    model = load_embedder()
    return model.encode(["query: " + q for q in queries], normalize_embeddings=True).astype(np.float32)

def save_index(index: faiss.Index, df: pd.DataFrame, csv_path: os.PathLike | str) -> None:
    # Persist FAISS index, mapping frame, and metadata for future reuse
    faiss.write_index(index, str(INDEX_DIR / "faq.index"))
    df.to_parquet(INDEX_DIR / "faq_mapping.parquet", index=False)
    meta = {
        "ts": time.time(),
        "rows": len(df),
        "csv_path": str(csv_path),
        "csv_mtime": os.path.getmtime(csv_path),
        "emb_model": EMB_MODEL,
    }
    with open(INDEX_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

# Runtime cache for in memory index and frame reuse
_RUNTIME: Dict[str, Any] = {}

def load_index() -> Tuple[pd.DataFrame, faiss.Index, Dict[str, Any]]:
    index = faiss.read_index(str(INDEX_DIR / "faq.index"))
    df = pd.read_parquet(INDEX_DIR / "faq_mapping.parquet")
    with open(INDEX_DIR / "meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    return df, index, meta

def get_store() -> Tuple[pd.DataFrame, faiss.Index, Dict[str, Any]]:
    # Load index and frame once and reuse through module lifetime
    if "df" not in _RUNTIME:
        df, index, meta = load_index()
        _RUNTIME["df"], _RUNTIME["index"], _RUNTIME["meta"] = df, index, meta
    return _RUNTIME["df"], _RUNTIME["index"], _RUNTIME["meta"]

def index_exists() -> bool:
    # Check for presence of index and mapping files
    return (INDEX_DIR / "faq.index").exists() and (INDEX_DIR / "faq_mapping.parquet").exists()

def is_index_outdated(csv_path: os.PathLike | str) -> bool:
    # Detect index staleness based on CSV modification time
    meta_path = INDEX_DIR / "meta.json"
    if not meta_path.exists():
        return True
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return meta.get("csv_mtime", 0) < os.path.getmtime(csv_path)

def build_index(csv_path: os.PathLike | str = CSV_PATH) -> Tuple[pd.DataFrame, faiss.Index]:
    print(f"Loading CSV: {csv_path}")
    df = read_csv_clean(csv_path)
    print("Encoding passages, first run may take longer.")
    emb = encode_passages(df["doc_text"].tolist())
    print("Building FAISS index.")
    index = faiss.IndexFlatIP(emb.shape[1])   # Inner product for cosine similarity with normalized embeddings
    index.add(emb)
    save_index(index, df, csv_path)
    print(f"Index stored under directory: {INDEX_DIR}")
    return df, index

# Build or refresh index on module import to keep it synchronized with CSV
if not index_exists() or is_index_outdated(CSV_PATH):
    _df, _index = build_index(CSV_PATH)
else:
    print("Existing index is current and ready to use.")

# Retrieval and routing functions
def retrieve(query: str, k: int = TOP_K) -> List[Dict[str, Any]]:
    df, index, meta = get_store()
    qv = encode_queries([query])
    D, I = index.search(qv, k)
    hits: List[Dict[str, Any]] = []
    for score, idx in zip(D[0], I[0]):
        row = df.iloc[int(idx)]
        hits.append({
            "score": float(score),
            "category": row["category"],
            "question": row["question"],
            "answer": row["answer"],
            "doc_text": row["doc_text"],
        })
    return hits

def deterministic_answer(hit: Dict[str, Any]) -> str:
    # Use the stored FAQ answer with minimal formatting logic
    base = hit["answer"].strip()
    if not base.endswith((".", "!", "?")):
        base += "."
    return base.strip()

def predict_category_knn(hits: List[Dict[str, Any]], k: int = 10) -> str:
    # Estimate category through majority vote among top candidates
    pool = hits[:k]
    cats = [h["category"] for h in pool]
    if not cats:
        return ""
    return max(set(cats), key=cats.count)

def log_interaction(payload: Dict[str, Any], log_path: Path = Path(LOG_PATH)) -> None:
    # Append structured interaction payload to a log file in JSON line format
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

# RAG integration with Ollama
def call_ollama(prompt: str, model: str = OLLAMA_MODEL, host: str = OLLAMA_HOST, timeout: int = 120) -> str:
    if not prompt or not str(prompt).strip():
        return "(Prompt ke Ollama kosong. Cek make_prompt atau contexts.)"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "num_ctx": 2048},  # Limit output length and context usage
        "keep_alive": "1h",
    }
    try:
        r = requests.post(f"{host}/api/generate", json=payload, timeout=timeout)
        if r.status_code == 200:
            txt = (r.json().get("response") or "").strip()
            return txt if txt else "(Ollama mengembalikan respons kosong.)"
        return f"(Ollama error: HTTP {r.status_code} - {r.text[:300]})"
    except Exception as e:  # noqa: BLE001 - broad exception is acceptable at I O boundary
        return f"(Ollama not reachable: {e})"

def make_prompt(user_q: str, contexts: List[Dict[str, Any]]) -> str:
    def clip(t: str, n: int = 600) -> str:
        return t[:n]
    ctx_text = "\n\n---\n".join([clip(c["doc_text"]) for c in contexts[:2]])
    return (
        "Anda adalah asisten FAQ pengadilan. "
        "Jawab ringkas (maks 1 paragraf) dalam bahasa Indonesia. "
        "Dasarkan jawaban HANYA pada KONTEKS di bawah. "
        "Jika konteks tidak memuat informasinya, katakan singkat bahwa konteks belum cukup dan minta klarifikasi.\n\n"
        "=== KONTEKS ===\n"
        f"{ctx_text}\n\n"
        "=== PERTANYAAN PENGGUNA ===\n"
        f"{user_q}\n\n"
        "=== PETUNJUK ===\n"
        "- Jangan mengada-ada di luar konteks.\n"
    )

def answer_question(q: str) -> Dict[str, Any]:
    hits = retrieve(q, k=TOP_K)
    if not hits:
        msg = (
            "Maaf, saya tidak bisa membantu untuk pertanyaan Anda."
        )
        log_interaction({"ts": time.time(), "question": q, "mode": "NO_HITS", "answer": msg})
        return {"mode": "NO_HITS", "answer": msg, "top_score": 0.0, "predicted_category": ""}

    top = hits[0]
    s = float(top["score"])
    pred_cat = predict_category_knn(hits)

    if s >= HIGH_THRESHOLD:
        out = deterministic_answer(top)
        log_interaction({
            "ts": time.time(), "question": q, "mode": "DETERMINISTIC", "top_score": s,
            "predicted_category": pred_cat, "used_categories": [h["category"] for h in hits[:3]],
        })
        return {"mode": "DETERMINISTIC", "answer": out, "top_score": s, "predicted_category": pred_cat}

    elif s >= LOW_THRESHOLD:
        if ENABLE_RAG:
            # RAG branch is intentionally preserved to follow the original behavior
            ctx = hits[:3]
            prompt = make_prompt(q, ctx)
            out = call_ollama(prompt)
            if not out or not out.strip() or out.startswith("("):
                # Lightweight fallback inside RAG branch that shows similar questions when generation fails
                suggest = "\n".join(f"- {h['question']}" for h in ctx)
                out = ("Saya belum bisa merangkum jawaban dari konteks.\n"
                       "Pertanyaan Anda mirip dengan:\n" + suggest)
            log_interaction({
                "ts": time.time(), "question": q, "mode": "RAG", "top_score": s,
                "predicted_category": pred_cat, "used_categories": [h["category"] for h in ctx],
            })
            return {"mode": "RAG", "answer": out, "top_score": s, "predicted_category": pred_cat}

    # Fallback branch when no reliable FAQ candidate is available
    # Specification requires that similar FAQ questions are not returned in this branch
    msg = (
        "Maaf, saya belum bisa menjawab pertanyaan Anda berdasarkan data yang ada. "
        "Silakan perjelas pertanyaan atau gunakan kata kunci lain."
    )
    log_interaction({
        "ts": time.time(), "question": q, "mode": "FALLBACK", "top_score": s,
        "predicted_category": pred_cat, "used_categories": [h["category"] for h in hits[:3]],
    })
    return {"mode": "FALLBACK", "answer": msg, "top_score": s, "predicted_category": pred_cat}

# Initialization helper to keep the index aligned with the latest CSV
def ensure_index_current(csv_path: os.PathLike | str = CSV_PATH) -> None:
    if not index_exists() or is_index_outdated(csv_path):
        print("CSV changed or index missing, rebuilding index.")
        build_index(csv_path)
    else:
        print("Index is up-to-date and ready.")

ensure_index_current(CSV_PATH)
