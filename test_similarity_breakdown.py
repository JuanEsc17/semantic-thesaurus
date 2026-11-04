import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
import difflib

data = json.load(open('domain/lel_hospital_2025.json', encoding='utf-8'))
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def get_emb(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        out = model(**inputs)
        mask = inputs['attention_mask'].unsqueeze(-1).expand(out.last_hidden_state.size()).float()
        sum_emb = torch.sum(out.last_hidden_state * mask, 1)
        counts = torch.clamp(mask.sum(1), min=1e-9)
        emb = sum_emb / counts
        return torch.nn.functional.normalize(emb, p=2, dim=1)

name_embs = get_emb([x['name'] for x in data])
notion_embs = get_emb([f"{x['name']}: {x['notion']}" for x in data])

sim_name = torch.mm(name_embs, name_embs.t()).numpy()
sim_notion = torch.mm(notion_embs, notion_embs.t()).numpy()

# Test acronym / subword overlap
def name_score(n1, n2):
    n1_l = n1.lower()
    n2_l = n2.lower()
    # check acronym
    words1 = [w[0] for w in n1_l.split() if w]
    words2 = [w[0] for w in n2_l.split() if w]
    acr1 = "".join(words1)
    acr2 = "".join(words2)
    if acr1 == n2_l or acr2 == n1_l:
        return 1.0
    return difflib.SequenceMatcher(None, n1_l, n2_l).ratio()

print("Doctor vs Physician:")
idx_doc = [i for i, x in enumerate(data) if x['name'] == 'Doctor'][0]
idx_phy = [i for i, x in enumerate(data) if x['name'] == 'Physician'][0]
idx_pat = [i for i, x in enumerate(data) if x['name'] == 'Patient'][0]

print("  Physician - Doctor: name_sim =", sim_name[idx_phy, idx_doc], "notion_sim =", sim_notion[idx_phy, idx_doc])
print("  Physician - Patient: name_sim =", sim_name[idx_phy, idx_pat], "notion_sim =", sim_notion[idx_phy, idx_pat])
print("  Doctor - Patient: name_sim =", sim_name[idx_doc, idx_pat], "notion_sim =", sim_notion[idx_doc, idx_pat])

