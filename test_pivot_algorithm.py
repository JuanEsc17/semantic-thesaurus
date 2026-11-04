import json
import torch
import numpy as np
import difflib
from transformers import AutoTokenizer, AutoModel

# Load data
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

names = [x['name'] for x in data]
types = [x['type'] for x in data]
notions = [f"{x['name']}: {x['notion']}" for x in data]

emb_names = get_emb(names)
emb_notions = get_emb(notions)

sim_names = torch.mm(emb_names, emb_names.t()).numpy()
sim_notions = torch.mm(emb_notions, emb_notions.t()).numpy()

def check_acronym(n1, n2):
    n1_l = n1.lower().replace("-", " ")
    n2_l = n2.lower().replace("-", " ")
    w1 = [w[0] for w in n1_l.split() if w]
    w2 = [w[0] for w in n2_l.split() if w]
    if "".join(w1) == n2_l or "".join(w2) == n1_l:
        return 1.0
    return 0.0

n = len(data)
sim_final = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        if i == j:
            sim_final[i, j] = 1.0
            continue
        # Only compare symbols of the exact same LEL type
        if types[i] != types[j]:
            sim_final[i, j] = 0.0
            continue
        
        acr = check_acronym(names[i], names[j])
        if acr > 0:
            sim_final[i, j] = 0.95
            continue
        
        # Combined score: weighted average of notion similarity and name similarity
        s_notion = float(sim_notions[i, j])
        s_name = float(sim_names[i, j])
        
        # Levenshtein ratio for fuzzy lexical similarity
        s_fuzzy = difflib.SequenceMatcher(None, names[i].lower(), names[j].lower()).ratio()
        
        score = 0.55 * s_notion + 0.35 * s_name + 0.10 * s_fuzzy
        sim_final[i, j] = score

# Paper's Algorithm: PivotTermDetermination
THRESHOLD = 0.68
TOP_K = 5

W_out = {}
for i in range(n):
    candidates = []
    for j in range(n):
        if i != j and sim_final[i, j] >= THRESHOLD:
            candidates.append((j, sim_final[i, j]))
    candidates.sort(key=lambda x: x[1], reverse=True)
    W_out[i] = candidates[:TOP_K]

W_in = {i: [] for i in range(n)}
for i, candidates in W_out.items():
    for rank, (j, score) in enumerate(candidates):
        W_in[j].append((i, rank, len(candidates), score))

inflow = np.zeros(n)
outflow = np.zeros(n)

for i in range(n):
    # Eq 3: outflow
    cand_out = W_out[i]
    nW = len(cand_out)
    for rank, (j, score) in enumerate(cand_out):
        g = (nW - rank) / nW
        outflow[i] += g * score
        
    # Eq 2: inflow
    for (src, rank_in_src, nW_src, score) in W_in[i]:
        g = (nW_src - rank_in_src) / nW_src
        inflow[i] += g * score

# Eq 4: Flow margin
flow_margin = inflow - outflow

# Pivot selection
pivot_terms = []
replacements = {}

for i in range(n):
    if len(W_out[i]) == 0 and len(W_in[i]) == 0:
        continue # Isolated term
    if flow_margin[i] > 0:
        pivot_terms.append(i)

for i in range(n):
    if len(W_out[i]) == 0 and len(W_in[i]) == 0:
        continue
    if flow_margin[i] <= 0:
        # Step 2: replace with similar word whose flow margin is positive
        best_pivot = None
        for j, score in W_out[i]:
            if flow_margin[j] > 0:
                best_pivot = j
                break
        if best_pivot is None and len(W_out[i]) > 0:
            best_pivot = W_out[i][0][0]
        if best_pivot is not None:
            replacements[i] = best_pivot

print(f"Total symbols with connections: {len([i for i in range(n) if len(W_out[i]) > 0 or len(W_in[i]) > 0])}")
print(f"Pivot Terms count: {len(pivot_terms)}")
print("\nPIVOT TERMS:")
for p in pivot_terms:
    print(f"  * [{types[p]}] {names[p]} (inflow={inflow[p]:.2f}, outflow={outflow[p]:.2f}, margin={flow_margin[p]:+.2f})")

print("\nREPLACEMENTS (Target -> Pivot Term):")
for src, dst in replacements.items():
    print(f"  * [{types[src]}] {names[src]} ---> USE ---> {names[dst]} (sim={sim_final[src, dst]:.2f})")

