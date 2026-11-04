# Standardized 2024 LEL datasets

These files were extracted from the 2024 TTPS Word documents and normalized to
the same JSON schema as `data/raw/lel_01.json`:

```json
{
    "name": "Symbol name in English",
    "type": "Subject | Object | Verb | State",
    "notion": "Notion in English",
    "impact": "Impact in English"
}
```

Only symbols with a complete LEL definition (name, category, notion, and
impact) were included. Summary symbol lists and scenarios were excluded.
Duplicate definitions within the same source document were collapsed. Original
Word documents were not modified.

| Output | Source | Symbols |
|---|---|---:|
| `lel_ttps_group_01.json` | 2024 TTPS group 01 | 32 |
| `lel_ttps_group_02.json` | 2024 TTPS group 02 | 22 |
| `lel_ttps_group_03.json` | 2024 TTPS group 03 | 37 |
| `lel_ttps_group_04.json` | 2024 TTPS group 04 | 47 |
| `lel_ttps_group_05.json` | 2024 TTPS group 05 | 4 |
| `lel_tomato_2024.json` | 2024 tomato-growing LEL and scenarios | 4 |
| `lel_hospital_2025.json` | Hospital Management (Roldán Valdiviezo / UNLP 2025 + LLM expansion) | 51 |
| `lel_military_2025.json` | Military Academy Discipline (Roldán Valdiviezo / UNLP 2025 + LLM expansion) | 61 |
| `lel_genetic_lab_2024.json` | Genetic Lab Workflow (Consolidated TTPS 2024 Groups 01-04) | 112 |

Translations and standardizations received a terminology review.
Names were normalized for domain consistency, but the notion and impact retain
the meaning, categories, and level of detail of each source document.
Explicit synonyms documented across independent stakeholders and expanded via LLM
are preserved as separate symbols to provide grounded evaluation pairs for synonym detection.
Companion ground truth positive pairs are tracked in:
- `data/pairs/hospital_ground_truth_pairs.json` (22 seeded positive pairs)
- `data/pairs/military_ground_truth_pairs.json` (28 seeded positive pairs)
- `data/pairs/genetic_lab_ground_truth_pairs.json` (9 cross-group positive pairs)
- `data/pairs/tomato_ground_truth_pairs.json` (21 scenario-derived positive pairs)



