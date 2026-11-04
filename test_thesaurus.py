import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel

data = json.load(open('domain/lel_hospital_2025.json', encoding='utf-8'))
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# Create texts for each symbol: name + notion + impact
texts = [f"{x['name']} ({x['type']}): {x['notion']} {x['impact']}" for x in data]
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
with torch.no_grad():
    out = model(**inputs)
    mask = inputs['attention_mask'].unsqueeze(-1).expand(out.last_hidden_state.size()).float()
    sum_emb = torch.sum(out.last_hidden_state * mask, 1)
    counts = torch.clamp(mask.sum(1), min=1e-9)
    emb = sum_emb / counts
    emb = torch.nn.functional.normalize(emb, p=2, dim=1)

sim_matrix = torch.mm(emb, emb.t()).numpy()

# Check top pairs of same type
pairs = []
for i in range(len(data)):
    for j in range(i+1, len(data)):
        if data[i]['type'] == data[j]['type']:
            score = float(sim_matrix[i, j])
            if score >= 0.70:
                pairs.append((score, data[i]['name'], data[j]['name'], data[i]['type']))

pairs.sort(reverse=True)
print(f'Total pairs >= 0.70 (same type): {len(pairs)}')
for score, n1, n2, t in pairs[:25]:
    print(f'{score:.3f} | [{t}] {n1} <---> {n2}')

