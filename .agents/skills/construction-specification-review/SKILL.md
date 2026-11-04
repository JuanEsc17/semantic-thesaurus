---
name: construction-specification-review
description: Specialist in automated construction specification review, semantic construction thesauri, NLP keyword extraction (ORG, ACT, ELM, STD, REF), and provision pairing based on the LIFIA/SNU research framework (Moon et al., 2022).
---

# Construction Specification Review & Semantic Thesaurus Skill

This skill operationalizes the research methodology from *"Automated system for construction specification review using natural language processing"* (Moon, Lee, & Chi, *Advanced Engineering Informatics*, 2022), located in the project's `docs/` folder.

## Core Purpose

Assist researchers, civil engineers, and developers in building and operating automated review systems for technical construction specifications, resolving semantic conflicts across multi-jurisdictional standards (e.g., Qatar QCS, US State DOTs, Australian Standards, Eurocodes).

---

## 1. Research Framework & Core Components

```
[ Unstructured PDF/TXT Specifications ]
                 │
                 ▼
 ┌───────────────────────────────────────────────────────────┐
 │ 1. Semantic Construction Thesaurus                        │
 │    - Word2Vec (Skip-gram, dim=200, window=10)             │
 │    - PivotTermDetermination algorithm (Inflow/Outflow)    │
 │    - Resolves synonym/lemma variance & circular loops     │
 └─────────────────────────────┬─────────────────────────────┘
                               │
 ┌─────────────────────────────▼─────────────────────────────┐
 │ 2. Requirement Keyword Recognition (NER)                  │
 │    - 5 Target Entities: ORG, ACT, ELM, STD, REF           │
 │    - Architecture: Word2Vec + Bi-LSTM + CRF               │
 └─────────────────────────────┬─────────────────────────────┘
                               │
 ┌─────────────────────────────▼─────────────────────────────┐
 │ 3. Relevant Provision Pairing                             │
 │    - Doc2Vec (PV-DBOW, dim=500, window=10)                │
 │    - Cosine similarity normalized: (cos + 1) / 2          │
 │    - Semantic relevance threshold >= 0.80                 │
 └─────────────────────────────┬─────────────────────────────┘
                               │
 ┌─────────────────────────────▼─────────────────────────────┐
 │ 4. Discrepancy Detection & Analysis Report                │
 │    - Cross-comparison of qualitative & quantitative rules │
 │    - Detection of site-incompatible provisions            │
 └───────────────────────────────────────────────────────────┘
```

---

## 2. Methodology & Implementation Guidelines

### A. Semantic Construction Thesaurus
- **Embedding Configuration**: Word2Vec Skip-gram (`vector_size=200`, `window=10`, `min_count=10`, `epochs=200`).
- **N-gram Tokenization**: Preserve domain-specific compounds of length $n=2$ to $5$ (e.g., `"job mix"`, `"tack coat"`, `"hot mix asphalt"`).
- **Custom Stopwords**: Filter out syntax tokens (`a`, `the`, `is`, `are`, `of`, `this`, `those`) without eliminating technical prepositions that alter requirement meaning.
- **Lemmatization**: Use lemmatization rather than stemming to preserve domain semantics (e.g., `bituminous` -> `bitumen`, `celsius` -> `celsius`).
- **PivotTermDetermination Algorithm**:
  1. Build a directed similar-word graph with cosine similarity $\ge 0.5$.
  2. Calculate flow margin for word $w$:
     $$f_w = \text{inflow}_w - \text{outflow}_w$$
  3. Words with $f_w > 0$ are designated as **pivot terms**.
  4. Replace non-pivot terms with their highest-similarity pivot term to avoid recursive conversion cycles (e.g., `tire` $\leftrightarrow$ `tyre` $\leftrightarrow$ `pneumatic`).

### B. Requirement Keyword Recognition (NER)
Extract the 5 primary risk-management information categories from each provision:
1. **ORG (Organization / Personnel)**: Roles and entities in charge (e.g., `Contractor`, `Engineer`, `Quality Manager`).
2. **ACT (Action / Activity)**: Mandatory or procedural verbs (e.g., `submit`, `test`, `compact`, `store`, `inspect`).
3. **ELM (Element / Item)**: Physical materials, construction elements, or structural items (e.g., `coarse aggregate`, `binder course`, `asphalt concrete`).
4. **STD (Standard / Criteria)**: Qualitative or quantitative thresholds (e.g., `12.5 mm`, `minimum 95%`, `temperature between 140°C and 160°C`).
5. **REF (Reference)**: External norms, testing methods, or cited national codes (e.g., `ASTM D6927`, `AASHTO T245`, `BS EN 12697`).

### C. Provision Pairing & Semantic Relevance
- Text units are analyzed at the **provision level** (a coherent clause sharing the lowest-level section heading).
- Embed provisions with Doc2Vec PV-DBOW (`vector_size=500`, `window=10`, `min_count=30`, `epochs=200`).
- Compute normalized semantic relevance:
  $$\text{Relevance}(p_1, p_2) = \frac{\cos(\mathbf{v}_{p_1}, \mathbf{v}_{p_2}) + 1}{2}$$
- **Threshold Rule**:
  - If $\max(\text{Relevance}) \ge 0.80$: Pair provisions for detailed keyword comparison.
  - If $\max(\text{Relevance}) < 0.80$: Label as `No Relevant Provision` (avoiding false-positive alignment).

---

## 3. Discrepancy & Non-Compliance Checking Rules

When comparing a project specification ($S_{\text{target}}$) against a national reference standard ($S_{\text{standard}}$):
1. **Environmental Incompatibility**: Flag criteria adopted from incompatible climates or geological environments (e.g., applying UK cold-climate temperature specs in desert climates).
2. **Standard Mismatch**: Detect provisions citing outdated, foreign, or conflicting testing codes (e.g., mixing ASTM and BS EN without cross-calibration).
3. **Tolerance Gaps**: Flag when quantitative values in $S_{\text{target}}$ are less stringent than mandatory minimum thresholds in $S_{\text{standard}}$.

