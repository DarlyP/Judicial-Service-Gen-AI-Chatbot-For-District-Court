![Personal Care Image](https://github.com/DarlyP/Judicial-Service-Gen-AI-Chatbot-For-District-Court/blob/main/readme_image/judical_ai.jpg)

# Judicial Service Gen AI Chatbot For District Court

---

## Tools
[<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />](https://pandas.pydata.org/)
[<img src="https://img.shields.io/badge/Looker%20Studio-4285F4?style=for-the-badge&logo=looker&logoColor=white" alt="Looker Studio" />](https://lookerstudio.google.com/)


---

## Data Source

[<img src="https://img.shields.io/badge/Badan%20Pusat%20Statistik-0093DD?style=for-the-badge&logoColor=white" alt="Badan Pusat Statistik" />](https://www.bps.go.id/)
[<img src="https://img.shields.io/badge/Tokopedia-42B549?style=for-the-badge&logo=tokopedia&logoColor=white" alt="Tokopedia" />](https://www.tokopedia.com/)
[<img src="https://img.shields.io/badge/Google%20Trends-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Trends" />](https://trends.google.com/trends/)


---

## Special Thanks to: 

[<img src="https://img.shields.io/badge/tokopaedi-Repository-24292e?style=for-the-badge&logo=github&logoColor=white" alt="tokopaedi repository" />](https://github.com/hilmiazizi/tokopaedi)
[<img src="https://img.shields.io/badge/Author-Hilmi%20Azizi-24292e?style=for-the-badge&logo=github&logoColor=white" alt="Author: Hilmi Azizi" />](https://github.com/hilmiazizi)

**Tokopaedi** is a Python library by **Hilmi Azizi** for programmatically extracting Tokopedia marketplace data: you can run filtered product searches (e.g., by price, rating, condition), fetch rich product details (variants, stock, media, and accurate mobile pricing), and collect customer reviews; results are dataclass-based and easy to serialize to JSON or load into pandas, and convenience helpers like a SearchResults container support enrich_details() and enrich_reviews() to auto-gather metadata and reviews at scale—installable via pip install tokopaedi and MIT-licensed.

---

## Introduction:

This report maps Indonesia’s skincare opportunity at the provincial level (2024–2025) and turns it into actionable decisions. We combine demand from Google Trends (geomap, timeline, related topics), supply & pricing from Tokopedia (price, sales, reviews, stock, price bands), and macro-demographics (Gini 2024, density 2021, UMP 2020, 2024 non-food spend, age structure). Using a Python (.ipynb) pipeline, we normalize data (province keys, types), engineer core metrics—interest_province, sold_per_100k, price_to_nonfood, demand_proxy—and synthesize them into a weighted Opportunity Score (0–100) that rewards demand & density and penalizes high supply and affordability burden. Key outputs (e.g., opportunity_score_by_province, province_master, tokopedia_agg_by_province, trends_geomap_summary, related_topics_clean) are exported to CSV and visualized in Looker. 

---

## Conclusion

* **Near-term upside:** Focus on provinces with **high search interest but low sales per 100k residents**; rapidly expand **listings, inventory, and retail media**, and introduce **trial packs at Rp20–35k** plus **value bundles**.
* **Mature markets (e.g., Central Java):** Prioritize **share defense** and **AOV lift** through **regimen bundles** and **step-up variants** (≈**Rp60–75k / Rp100–150k**).
* **Affordability lens:** Use the **price-to-non-food ratio** (median skincare price ÷ average monthly non-food spend per capita) as a gate:

  * **High ratios** (e.g., North Sulawesi) → push **trial/mini sizes, value bundles, light promos**.
  * **0.05–0.10 ratios** (e.g., Banten) → support **premium-lite and upsell** plays.
* **Price-band positioning:**

  * **DKI Jakarta:** Highest **premium (≥Rp200k ~26%)** → ready for **regimen bundles**.
  * **Banten:** **Mid-tier–heavy (Rp100–199k)** → use **mid-tier anchors + selective premium-lite**.
  * **West Java:** **Entry-led (<Rp50k)** with a **Rp100–199k layer** → **lead with value, then step up**.
  * **DI Yogyakarta:** **Mid-tier core** with a **small premium tail** → **test premium selectively**.
  * **Bali:** **50–99k-heavy** with **minimal premium (~1–2%)** → **lean into value/entry**.
* **Macro filters:** A **higher UMP** is supportive but must be cross-checked with **price-to-non-food ratio** and **sales per 100k**; a **high Gini** favors a **barbell assortment** (value + premium); **high population density** boosts reach but also competition.
* **Demographic focus:** Prioritize provinces that **combine high female 20–39 population per 100k with high interest**.
* **Execution waves:**

  * **Wave 1 (growth/gap):** High interest, **low sales per 100k**, **price-to-non-food ≤ 0.10** → **trial/value offers + problem-led creatives**.
  * **Wave 2 (mature/value):** High interest, **high sales per 100k** → **regimen bundles + step-up lines**.
* **Success metrics:** Track **Δ sales per 100k (treatment vs. control)** plus **ROAS, CTR, CVR, and AOV** to validate impact.


---

## Dashboard

**Looker Studio** : [Personal Care Go To Market (GTM)](https://lookerstudio.google.com/reporting/a1038cd1-10fa-4b3e-800c-9380352f54b7).

---

**Disclaimer**: 
- This notebook is created solely for learning and exploration purposes. There is no intention to offend or harm any party. All content and analysis presented are based on publicly available data online. I undertake this process to enhance my understanding of data analysis techniques and methodologies and hone my skills in implementing relevant algorithms and models within the context of data science learning. In conducting this analysis, I strive to maintain objectivity and professionalism in interpreting the existing data. Any conclusions or recommendations provided result from personal analysis and are not intended as professional advice in any specific capacity. I hope the information obtained from this notebook can be useful to anyone reading it to learn and develop data analysis skills.
