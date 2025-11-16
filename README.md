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
     - required columns: `category`, `question`, `answer`
     - question length & end with `?`
     - answer length range, no HTML, etc.

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
     - question input
     - quick “pill” examples
     - confidence badges
     - transparency: show similar FAQ rows
     - session history with feedback and export

---

## 🧩 Key Features

- 🔍 **Semantic FAQ search** with FAISS + multilingual E5 embeddings  
- 🎯 **Deterministic vs RAG routing** based on similarity thresholds  
- 🧾 **Session history dashboard** with:
  - bookmarks
  - 👍/👎 feedback
  - free-text notes
  - CSV export
- 📈 **Candidate FAQ pipeline**
  - low-confidence questions logged to `candidate_faq.csv`
  - includes suggested category, timestamps, and status
- ✅ **Data quality checks**
  - Great Expectations suite (`standar_layanan_suite_auto`)
  - summary stored in `validation_results_summary.csv`
- 🧱 **Local-first design**
  - no external API keys needed
  - can run fully inside court infrastructure

---

**Disclaimer**: 
- This notebook is created solely for learning and exploration purposes. There is no intention to offend or harm any party. All content and analysis presented are based on publicly available data online. I undertake this process to enhance my understanding of data analysis techniques and methodologies and hone my skills in implementing relevant algorithms and models within the context of data science learning. In conducting this analysis, I strive to maintain objectivity and professionalism in interpreting the existing data. Any conclusions or recommendations provided result from personal analysis and are not intended as professional advice in any specific capacity. I hope the information obtained from this notebook can be useful to anyone reading it to learn and develop data analysis skills.
