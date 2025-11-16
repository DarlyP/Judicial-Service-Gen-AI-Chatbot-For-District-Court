# Streamlit application for court information assistant backed by FAQ core
import time, json, io, csv
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

import faq_core as core  # Backend FAQ core module without explicit candidate suggestions

# Additional configuration for presentation and UI
# Header image can be a local path or a URL
HEADER_IMAGE = "Assets/header_kotabaru.jpg"

year = datetime.utcnow().year
FOOTER_TEXT = f"© {year} Pengadilan Negeri Kotabaru. All Rights Reserved"

# Fixed configuration that does not change retrieval logic
core.HIGH_THRESHOLD = 0.880
core.LOW_THRESHOLD  = 0.820
core.ENABLE_RAG = True
core.OLLAMA_HOST = "http://127.0.0.1:11434"
core.OLLAMA_MODEL = "gemma2:9b"
CSV_PATH = Path("Data/standar_layanan_combined.csv")

st.set_page_config(page_title="Asisten Informasi Pengadilan", layout="wide")

# Inline CSS styles for a user friendly layout
st.markdown(
    """
    <style>
    /* Layout padding so footer does not overlap content */
    main .block-container{padding-top:1rem; padding-bottom:100px}

    /* Hero title styling */
    .hero{font-size:2rem;font-weight:800;margin:.25rem 0 .5rem;
      background:linear-gradient(90deg,#0ea5e9,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}

    /* Header image wrapper styling */
    .header-wrap{border:1px solid rgba(148,163,184,.25);border-radius:16px;
      padding:8px;background:rgba(2,6,23,.03);margin-bottom:12px}
    .header-img{width:100%;height:auto;border-radius:12px;display:block}

    /* Badge appearance */
    .badge{display:inline-block;padding:4px 10px;border-radius:999px;font-size:.80rem;font-weight:600;margin-right:6px}
    .b-ok{background:#dcfce7;color:#166534}.b-mid{background:#fef3c7;color:#92400e}.b-low{background:#fee2e2;color:#991b1b}

    /* Card container */
    .card{border:1px solid rgba(148,163,184,.25);border-radius:14px;padding:16px 18px;background:rgba(2,6,23,.03); margin-bottom:10px}
    .meta{color:#475569;font-size:.85rem}
    .small{color:#64748b;font-size:.85rem}

    /* Button spacing for sample question pills */
    .pills button{margin-right:8px;margin-bottom:6px}

    /* Fixed footer styling */
    .app-footer{position:fixed;left:0;right:0;bottom:0;z-index:1000;
      background:rgba(2,6,23,.85);backdrop-filter: blur(6px);
      color:#94a3b8;border-top:1px solid rgba(148,163,184,.25);
      padding:10px 16px;text-align:center;font-size:.9rem}

    /* Subtle hover effect for buttons */
    button[kind="primary"], .stButton>button{border-radius:12px}
    .stButton>button:hover{filter:brightness(1.05)}
    </style>
    """,
    unsafe_allow_html=True,
)

# Display header image
st.image(HEADER_IMAGE)

# Title and subtitle
st.markdown('<div class="hero">Asisten Informasi Pengadilan</div>', unsafe_allow_html=True)
st.caption("Tanya apa pun tentang layanan. Kami jawab singkat & jelas.")

# Initialization and warm up for index and model
with st.spinner("Menyiapkan…"):
    core.ensure_index_current(str(CSV_PATH))
    try:
        # Lightweight warm up call to Ollama to reduce first response latency
        requests.post(
            f"{core.OLLAMA_HOST}/api/generate",
            json={"model": core.OLLAMA_MODEL, "prompt": "OK", "stream": False,
                  "options": {"temperature": 0, "num_predict": 1}},
            timeout=10
        )
    except Exception:
        pass

# Sample question helper for quick user exploration
def sample_questions(n=6):
    try:
        df = pd.read_csv(CSV_PATH)
        ex = df["question"].dropna().astype(str).str.strip().sample(min(n, len(df)), random_state=42).tolist()
        return ex
    except Exception:
        # Fallback examples used when CSV cannot be read
        return [
            "Apa syarat mengajukan gugatan perdata?",
            "Kapan loket praperadilan buka?",
            "Berapa biaya pendaftaran perkara?",
            "Bagaimana cara mendaftar e-court?",
            "Apa itu PTSP dan layanan yang tersedia?",
            "Bagaimana cara memohon salinan putusan?"
        ]

st.write("Contoh cepat:")
examples = sample_questions(6)
pill_cols = st.columns(6)
for i, qex in enumerate(examples):
    with pill_cols[i % 6]:
        if st.button(qex, use_container_width=True, key=f"ex_{i}"):
            st.session_state.q = qex

# Main question input area
q = st.text_area(
    "Pertanyaan Anda",
    value=st.session_state.get("q",""),
    height=250,
    placeholder="Butuh informasi layanan? Tanyakan: “Bagaimana cara memohon salinan putusan?”"
)
st.markdown(f"<span class='small'>Panjang pertanyaan: {len(q)} karakter</span>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1,1,2])
with c1:
    run = st.button("Tanya", use_container_width=True)
with c2:
    if st.button("Hapus", use_container_width=True):
        st.session_state.q = ""
        st.rerun()

# UI helpers for confidence and metadata text
def confidence_badge(score: float) -> str:
    if score is None: return '<span class="badge b-low">Keyakinan: rendah</span>'
    if score >= core.HIGH_THRESHOLD: return '<span class="badge b-ok">Keyakinan: tinggi</span>'
    if score >= core.LOW_THRESHOLD:  return '<span class="badge b-mid">Keyakinan: sedang</span>'
    return '<span class="badge b-low">Keyakinan: rendah</span>'


def mode_microcopy(mode: str) -> str:
    m = (mode or "").upper()
    if m == "DETERMINISTIC": return "Jawaban langsung dari basis FAQ."
    if m == "RAG":           return "Diringkas dari dokumen terkait."
    if m == "FALLBACK":      return "Belum ada jawaban pasti. Tambahkan detail."
    if m == "NO_HITS":       return "Topik belum ditemukan."
    return ""


def last_updated_text():
    meta = Path(core.INDEX_DIR / "meta.json")
    if meta.exists():
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
            ts = pd.to_datetime(m.get("ts", None), unit="s", utc=True).tz_localize(None)
            return f"Terakhir diperbarui: {ts.date()} · {m.get('rows',0)} entri"
        except Exception:
            pass
    return "Terakhir diperbarui: —"


def rel_time(ts: float) -> str:
    d = max(0, time.time() - ts)
    if d < 60:   return f"{int(d)} dtk lalu"
    if d < 3600: return f"{int(d//60)} mnt lalu"
    if d < 86400:return f"{int(d//3600)} jam lalu"
    return f"{int(d//86400)} hari lalu"

# Session scoped history storage
if "history" not in st.session_state:
    st.session_state.history = []  # List of dictionaries representing Q and A records

def add_history(item: dict):
    # Normalize history entry with default fields
    item.setdefault("ts", time.time())
    item.setdefault("bookmarked", False)
    item.setdefault("feedback", None)  # "up" or "down" or None
    item.setdefault("note", "")
    st.session_state.history.append(item)

# Question processing and answer rendering
if run:
    if not q.strip():
        st.warning("Tolong isi pertanyaan terlebih dahulu.")
    else:
        t0 = time.time()
        with st.spinner("Mencari jawaban…"):
            res = core.answer_question(q)
        elapsed = time.time() - t0

        # Answer card with metadata and confidence display
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            f"""{confidence_badge(res.get('top_score',0.0))}
            <span class=\"meta\">{mode_microcopy(res.get('mode'))} · Waktu {elapsed:.2f}s · {last_updated_text()}</span>""",
            unsafe_allow_html=True
        )
        st.markdown("<br/>", unsafe_allow_html=True)
        st.write(res.get("answer","(tidak ada jawaban)"))
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick follow up actions for refinement and feedback
        colA, colB = st.columns([1,1])
        with colA:
            if st.button("Pertanyaan lanjutan", help="Tambahkan detail: jenis layanan, lokasi, waktu."):
                st.session_state.q = (q.strip() + " — Tambahkan: jenis layanan, lokasi, waktu, nomor perkara (bila ada).").strip()
                st.rerun()
        with colB:
            f1, f2 = st.columns([1,1])
            with f1:
                if st.button("👍 Membantu"):
                    st.toast("Terima kasih atas tanggapannya! 🙌")
            with f2:
                if st.button("👎 Kurang pas"):
                    st.info("Baik, silakan tambahkan detail agar jawaban lebih tepat.")

        # Transparent view into similar references used by the system
        with st.expander("Lihat referensi serupa"):
            similar = core.retrieve(q, k=3)
            df_sim = pd.DataFrame([{
                "Kategori": h["category"],
                "Pertanyaan serupa": h["question"],} for h in similar])
            st.dataframe(df_sim, use_container_width=True, hide_index=True)

        # Persist the interaction into session history
        add_history({
            "Pertanyaan": q,
            "Jawaban": res.get("answer",""),
            "Mode": res.get("mode",""),
            "Skor": float(res.get("top_score",0.0)),
            "Kategori": res.get("predicted_category",""),
            "Waktu (s)": elapsed
        })

# Session history as interactive cards instead of a plain table
st.subheader("Riwayat sesi")

# History toolbar for search, filter, sort, export and cleanup
tb1, tb2, tb3, tb4, tb5 = st.columns([2,1,1,1,1])
with tb1:
    q_search = st.text_input("Cari", placeholder="Ketik kata di pertanyaan/jawaban…")
with tb2:
    view = st.selectbox("Tampilan", ["Semua", "Ditandai ⭐", "Membantu 👍", "Kurang pas 👎"])
with tb3:
    newest_first = st.toggle("Terbaru dulu", value=True)
with tb4:
    if st.button("Hapus duplikat"):
        seen = set(); cleaned = []
        for r in st.session_state.history:
            key = (r.get("Pertanyaan", "").strip().lower(), r.get("Kategori", ""))
            if key in seen: continue
            seen.add(key); cleaned.append(r)
        st.session_state.history = cleaned
        st.success("Duplikat dibersihkan.")
with tb5:
    if st.session_state.history:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["ts","Pertanyaan","Jawaban","Mode","Skor","Kategori","Waktu (s)","bookmarked","feedback","note"])
        writer.writeheader()
        for r in st.session_state.history: writer.writerow(r)
        st.download_button("Unduh CSV", buf.getvalue().encode("utf-8"),
                           file_name="riwayat_faq.csv", mime="text/csv")

# Apply history filters and sort order based on toolbar state
rows = list(st.session_state.history)
if q_search:
    ql = q_search.strip().lower()
    rows = [r for r in rows if (ql in r.get("Pertanyaan",""
                    ).lower() or ql in r.get("Jawaban",""
                    ).lower())]
if view == "Ditandai ⭐":
    rows = [r for r in rows if r.get("bookmarked")]
elif view == "Membantu 👍":
    rows = [r for r in rows if r.get("feedback") == "up"]
elif view == "Kurang pas 👎":
    rows = [r for r in rows if r.get("feedback") == "down"]

rows.sort(key=lambda r: ((not r.get("bookmarked", False)), r.get("ts", 0)), reverse=newest_first)

# Renderer used for each history card
def render_card(idx: int, r: dict):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    # Header section with question and confidence badge
    h1, h2 = st.columns([4,2])
    with h1:
        st.markdown(f"**{r.get('Pertanyaan','(tanpa pertanyaan)')}**")
    with h2:
        sk = float(r.get("Skor", 0.0))
        if sk >= core.HIGH_THRESHOLD: badge = '<span class="badge b-ok">Keyakinan: tinggi</span>'
        elif sk >= core.LOW_THRESHOLD: badge = '<span class="badge b-mid">Keyakinan: sedang</span>'
        else: badge = '<span class="badge b-low">Keyakinan: rendah</span>'
        st.markdown(f'{badge} <span class="meta">· {rel_time(r.get("ts", time.time()))}</span>',
                    unsafe_allow_html=True)
    # Main answer body text
    st.write(r.get("Jawaban",""))
    # Action row for reuse, follow up, bookmark, feedback, and notes
    a1, a2, a3, a4, a5 = st.columns([1,1,1,1,3])
    with a1:
        if st.button("Tanya ulang", key=f"reh_{idx}"):
            st.session_state.q = r.get("Pertanyaan","")
            st.rerun()
    with a2:
        if st.button("Lanjutkan", key=f"fu_{idx}"):
            base = r.get("Pertanyaan","")
            st.session_state.q = base + " — Tambahkan detail: jenis layanan, lokasi, waktu, nomor perkara (bila ada)."
            st.rerun()
    with a3:
        mark_label = "⭐ Batalkan" if r.get("bookmarked") else "⭐ Tandai"
        if st.button(mark_label, key=f"bm_{idx}"):
            r["bookmarked"] = not r.get("bookmarked")
            st.rerun()
    with a4:
        c_up, c_down = st.columns(2)
        if c_up.button("👍", key=f"up_{idx}"):
            r["feedback"] = "up"; st.rerun()
        if c_down.button("👎", key=f"down_{idx}"):
            r["feedback"] = "down"; st.rerun()
    with a5:
        r["note"] = st.text_input("Catatan Anda (opsional)", value=r.get("note",""), key=f"note_{idx}")
    st.markdown('</div>', unsafe_allow_html=True)

# Render at most twelve cards per view for performance reasons
for i, row in enumerate(rows[:12]):
    render_card(i, row)

# Fixed footer with copyright text
st.markdown(f"<div class='app-footer'>{FOOTER_TEXT}</div>", unsafe_allow_html=True)
