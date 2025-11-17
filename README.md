![Personal Care Image](https://github.com/DarlyP/Judicial-Service-Gen-AI-Chatbot-For-District-Court/blob/main/readme_image/judical_ai.jpg)

# Judicial Service Gen AI Chatbot For District Court

---

## Tools
[<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />](https://www.python.org/)
[<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />](https://streamlit.io/)
[<img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama" />](https://ollama.com/)
[<img src="https://img.shields.io/badge/FAISS-005571?style=for-the-badge&logoColor=white" alt="FAISS" />](https://github.com/facebookresearch/faiss)

---

## Data Source

[<img src="https://img.shields.io/badge/Court%20Service%20Standards-Supreme%20Court%20of%20Indonesia-0F766E?style=for-the-badge" alt="Court Service Standards - Supreme Court of Indonesia" />](#)

---

## Deployment

**Hugging Face** : [Judicial Service Gen AI Chatbot For District Court](https://huggingface.co/spaces/darly9991/Kotabaru_Court_Chatbot).

---

## Introduction:

This repository contains a **judicial service chatbot** designed for **district courts in Indonesia**.  
The chatbot answers questions about court services — including civil, criminal, legal aid, public information, and general administration — using curated **FAQ CSV files** as its knowledge base, rather than the open internet. This approach keeps responses focused, auditable, and aligned with officially maintained service standards.

From an organisational perspective, the project demonstrates how modern AI can be applied in a **controlled, compliant, and explainable** way inside the justice sector. Instead of a generic chatbot, it delivers a domain-specific assistant that is:
- **Safe by design** – runs on local infrastructure (via a local LLM) with no citizen data sent to third-party cloud APIs.  
- **Policy-driven** – all answers trace back to structured court service documents that can be reviewed and updated by authorised staff.  
- **Citizen-oriented** – provides clear, consistent information to court users, helping to reduce repetitive front-desk questions and call volume.

---

## Key goals:

- 🛡️ **Privacy-first**: runs on **local LLM** via [Ollama](https://ollama.com)  
- 🇮🇩 **Indonesian-focused**: tuned for Bahasa Indonesia service FAQs  
- ⚖️ **Court-specific**: domain is *only* court procedures and public services  
- 📊 **Data-quality-aware**: validated with [Great Expectations](https://greatexpectations.io)

---
## 🧠 Architecture Overview

Pipeline at a glance:

1. **Structured FAQ data**
   - CSVs per service area:
     - `standar_layanan_hukum.csv`
     - `standar_layanan_perdata.csv`
     - `standar_layanan_pidana.csv`
     - `standar_layanan_umum.csv`
     - `FAQ_informasi_umum.csv`
   - Combined into `standar_layanan_combined.csv`.

2. **Data validation**
   - `great_expectations` checks:
     - Required columns: `category`, `question`, `answer`
     - Question length & end with `?`
     - Answer length range, no HTML, etc.

3. **Semantic index (FAISS)**
   - Embeddings: `intfloat/multilingual-e5-small`
   - Normalized vectors stored in a FAISS `IndexFlatIP`.

4. **Three-lane routing logic**

   | Lane           | Condition                    | Behaviour                                           |
   |----------------|------------------------------|-----------------------------------------------------|
   | DETERMINISTIC  | score ≥ HIGH_THRESHOLD       | Return CSV answer *as-is*                           |
   | RAG            | LOW_THRESHOLD ≤ score < HIGH | Use local LLM + FAQ context to summarize            |
   | FALLBACK       | score < LOW_THRESHOLD        | Show polite fallback, log as candidate FAQ          |

5. **Local LLM (RAG)**
   - Backend: [Ollama](https://ollama.com)
   - Example model: `llama3.2:3b-instruct-q4_K_M` or `qwen2.5:7b`

6. **User interface**
   - Frontend: [Streamlit](https://streamlit.io)
   - Features:
     - Question input
     - Quick “pill” examples
     - Confidence badges
     - Transparency: show similar FAQ rows
     - Session history with feedback and export

---

## 🧩 Key Features

- 🔍 **Semantic FAQ search** with FAISS + multilingual E5 embeddings  
- 🎯 **Deterministic vs RAG routing** based on similarity thresholds  
- 🧾 **Session history dashboard** with:
  - Bookmarks
  - 👍/👎 feedback
  - Free-text notes
  - CSV export
- 📈 **Candidate FAQ pipeline**
  - Low-confidence questions logged to `candidate_faq.csv`
  - Includes suggested category, timestamps, and status
- ✅ **Data quality checks**
  - Great Expectations suite (`standar_layanan_suite_auto`)
  - Summary stored in `validation_results_summary.csv`
- 🧱 **Local-first design**
  - No external API keys needed
  - Can run fully inside the court infrastructure

---

## Current Limitations

To keep the prototype focused and safe for a court environment, this project intentionally has a few limitations that are important to understand:

1. **No true conversational memory (yet)**  
   Each question is answered independently. The backend function `answer_question(q)` only sees the current user query and FAQ context; it does **not** maintain a multi-turn chat history at the LLM level.  
   - Follow-up questions, such as “How about for civil cases?” will only be answered correctly if the user repeats enough context in the new question.  
   - Session history is stored in the Streamlit UI for the user’s convenience, but it is not yet fed back into the RAG prompt.

2. **Knowledge is limited to curated FAQ CSVs**  
   The chatbot only answers based on the data in `standar_layanan_combined.csv` (and its source CSVs). Topics outside those service standards will trigger low similarity scores and fall into the fallback branch.  
   - This is a deliberate design choice to keep answers auditable and aligned with official documents.  
   - It also means the system will sometimes say “I cannot help” instead of guessing.

3. **Candidate FAQ pipeline is manual by design**  
   Low-confidence questions are logged to `candidate_faq.csv`, but they do not automatically update the main FAQ dataset.  
   - Court staff still need to review, edit, and approve new questions and answers before they are merged into the official CSV.  
   - This slows down fully automatic “learning”, but keeps human oversight in the loop.

4. **No automatic retraining schedule**  
   The FAISS index is rebuilt when the CSV changes (based on file timestamps), but there is no scheduled job or orchestration layer (e.g. Airflow, Prefect) in this repository. Operationalization (cron jobs, CI/CD, monitoring) is left to the deployment environment.

5. **Model and threshold choices are conservative**  
   Thresholds for `DETERMINISTIC`, `RAG`, and `FALLBACK` routing, as well as the default embedding model and LLM, are tuned for safety and clarity rather than maximum creativity.  
   - In some borderline cases, the system prefers to fall back and log a candidate FAQ instead of producing a speculative answer.  
   - These parameters can be adjusted, but should be reviewed carefully from a risk and governance perspective.

6. **Does not replace official legal advice**  
   Even with good data and routing, this chatbot is **not a legal expert system** and must not be treated as a source of binding legal interpretation.  
   - All responses should be considered informational and must be validated against current regulations and court policies.  
   - Any production deployment should include clear user-facing disclaimers and escalation paths to human officers.

These limitations are intentional for a first iteration in a judicial context. They also define a clear roadmap: introducing controlled conversational memory, expanding and curating the FAQ corpus, and integrating the system into existing court IT governance and monitoring processes.

---

**Disclaimer**: 
- This notebook is created solely for learning and exploration purposes. There is no intention to offend or harm any party. All content and analysis presented are based on publicly available data online. I undertake this process to enhance my understanding of data analysis techniques and methodologies and hone my skills in implementing relevant algorithms and models within the context of data science learning. In conducting this analysis, I strive to maintain objectivity and professionalism in interpreting the existing data. Any conclusions or recommendations provided result from personal analysis and are not intended as professional advice in any specific capacity. I hope the information obtained from this notebook can be useful to anyone reading it to learn and develop data analysis skills.
