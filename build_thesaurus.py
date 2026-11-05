"""
Thesaurus Builder based on Semantic Embeddings and Pivot Term Determination
(Moon, Lee & Chi, 2022 - Advanced Engineering Informatics)

Processes LEL (Language Extended Lexicon) datasets from `domain/` and generates
a structured, visualizable thesaurus with Pivot Terms, Synonyms, and SKOS metadata.
"""

import os
import json
import glob
import math
import difflib
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print(f"Loading transformer model: {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()

def get_embeddings(texts, batch_size=32):
    """Computes mean-pooled, normalized sentence embeddings."""
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            out = model(**inputs)
            mask = inputs["attention_mask"].unsqueeze(-1).expand(out.last_hidden_state.size()).float()
            sum_emb = torch.sum(out.last_hidden_state * mask, 1)
            counts = torch.clamp(mask.sum(1), min=1e-9)
            emb = sum_emb / counts
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            all_embs.append(emb.cpu().numpy())
    return np.vstack(all_embs)

def check_acronym(n1, n2):
    """Checks if one term is an exact acronym of the other."""
    n1_clean = n1.lower().replace("-", " ").replace("/", " ")
    n2_clean = n2.lower().replace("-", " ").replace("/", " ")
    w1 = [w[0] for w in n1_clean.split() if w]
    w2 = [w[0] for w in n2_clean.split() if w]
    acr1 = "".join(w1)
    acr2 = "".join(w2)
    if (len(acr1) >= 2 and acr1 == n2_clean) or (len(acr2) >= 2 and acr2 == n1_clean):
        return True
    return False

def compute_similarity_matrix(symbols, name_embs, notion_embs):
    """
    Computes pairwise semantic similarity between symbols.
    Combines concept notion similarity, name semantic similarity, acronym matching, and fuzzy string similarity.
    Enforces LEL grammatical type compatibility (Subject with Subject, Object with Object, etc.).
    """
    n = len(symbols)
    sim_names = np.dot(name_embs, name_embs.T)
    sim_notions = np.dot(notion_embs, notion_embs.T)
    
    sim_final = np.zeros((n, n), dtype=np.float32)
    
    for i in range(n):
        sim_final[i, i] = 1.0
        for j in range(i + 1, n):
            # Only compare symbols of compatible LEL types
            if symbols[i]["type"] != symbols[j]["type"]:
                continue
            
            n1 = symbols[i]["name"]
            n2 = symbols[j]["name"]
            
            # Acronym match: near-certain synonym
            if check_acronym(n1, n2):
                score = 0.96
            else:
                s_notion = float(sim_notions[i, j])
                s_name = float(sim_names[i, j])
                s_fuzzy = difflib.SequenceMatcher(None, n1.lower(), n2.lower()).ratio()
                
                # Weighted combination
                score = 0.52 * s_notion + 0.38 * s_name + 0.10 * s_fuzzy
            
            sim_final[i, j] = score
            sim_final[j, i] = score
            
    return sim_final

def run_pivot_term_determination(symbols, sim_matrix, threshold=0.68, top_k=5):
    """
    Implements the PivotTermDetermination algorithm from Moon, Lee & Chi (2022).
    
    Equations:
      (1) g(w', W) = (n(W) - index(w'|sorted(W))) / n(W)
      (2) inflow_w = sum_{w' in W_in} g(w', W_out(w')) * c(w, w')
      (3) outflow_w = sum_{w' in W_out} g(w', W_out(w)) * c(w, w')
      (4) fw = inflow_w - outflow_w
    """
    n = len(symbols)
    
    # 1. Build candidate similar word lists W_out
    W_out = {}
    for i in range(n):
        candidates = []
        for j in range(n):
            if i != j and sim_matrix[i, j] >= threshold:
                candidates.append((j, float(sim_matrix[i, j])))
        candidates.sort(key=lambda x: x[1], reverse=True)
        W_out[i] = candidates[:top_k]
        
    # 2. Build inflow references W_in
    W_in = {i: [] for i in range(n)}
    for i, candidates in W_out.items():
        for rank, (j, score) in enumerate(candidates):
            W_in[j].append((i, rank, len(candidates), score))
            
    # 3. Compute inflow, outflow, and flow margin
    inflow = np.zeros(n, dtype=np.float32)
    outflow = np.zeros(n, dtype=np.float32)
    
    for i in range(n):
        cand_out = W_out[i]
        nW = len(cand_out)
        for rank, (j, score) in enumerate(cand_out):
            g = (nW - rank) / nW
            outflow[i] += g * score
            
        for (src, rank_in_src, nW_src, score) in W_in[i]:
            g = (nW_src - rank_in_src) / nW_src
            inflow[i] += g * score
            
    flow_margin = inflow - outflow
    
    # 4. Connected components / Clusters identification
    # To resolve symmetric ties (where f_w1 == f_w2 == 0) deterministically:
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j, score in W_out[i]:
            adj[i].add(j)
            adj[j].add(i)
            
    # BFS to find connected components
    visited = set()
    components = []
    for i in range(n):
        if i not in visited and (len(W_out[i]) > 0 or len(W_in[i]) > 0):
            comp = []
            queue = [i]
            visited.add(i)
            while queue:
                curr = queue.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(comp)
            
    # For each component, select the dominant Pivot Term
    node_to_pivot = {}
    pivot_set = set()
    
    for comp in components:
        # Sort component nodes by:
        # 1. Flow margin (descending)
        # 2. Inflow (descending)
        # 3. Shorter name length (simpler canonical term)
        # 4. Alphabetical
        comp.sort(key=lambda idx: (
            flow_margin[idx],
            inflow[idx],
            -len(symbols[idx]["name"]),
            symbols[idx]["name"]
        ), reverse=True)
        
        pivot_idx = comp[0]
        pivot_set.add(pivot_idx)
        
        for idx in comp:
            node_to_pivot[idx] = pivot_idx
            
    # Replacement rules table
    replacement_rules = []
    for i in range(n):
        if i in node_to_pivot and node_to_pivot[i] != i:
            pivot_idx = node_to_pivot[i]
            sim_score = float(sim_matrix[i, pivot_idx])
            replacement_rules.append({
                "target_index": i,
                "target_name": symbols[i]["name"],
                "target_type": symbols[i]["type"],
                "pivot_index": pivot_idx,
                "pivot_name": symbols[pivot_idx]["name"],
                "pivot_type": symbols[pivot_idx]["type"],
                "similarity": round(sim_score, 4),
                "target_margin": round(float(flow_margin[i]), 3),
                "pivot_margin": round(float(flow_margin[pivot_idx]), 3)
            })
            
    # Compile node metadata
    node_metadata = []
    for i, s in enumerate(symbols):
        is_pivot = (i in pivot_set)
        pivot_idx = node_to_pivot.get(i, i)
        
        # UF (Used For) if pivot
        used_for = []
        if is_pivot:
            for cand_idx, p_idx in node_to_pivot.items():
                if p_idx == i and cand_idx != i:
                    used_for.append({
                        "name": symbols[cand_idx]["name"],
                        "similarity": round(float(sim_matrix[cand_idx, i]), 4)
                    })
                    
        node_metadata.append({
            "id": i,
            "name": s["name"],
            "type": s["type"],
            "notion": s["notion"],
            "impact": s["impact"],
            "is_pivot": is_pivot,
            "pivot_id": pivot_idx,
            "pivot_name": symbols[pivot_idx]["name"],
            "inflow": round(float(inflow[i]), 3),
            "outflow": round(float(outflow[i]), 3),
            "flow_margin": round(float(flow_margin[i]), 3),
            "has_connections": (i in node_to_pivot),
            "used_for": used_for
        })
        
    # Compile edges
    edges = []
    edge_set = set()
    for i in range(n):
        for j, score in W_out[i]:
            edge_key = (min(i, j), max(i, j))
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                
                # Check direction (Variant -> Pivot)
                p_i = node_to_pivot.get(i, i)
                p_j = node_to_pivot.get(j, j)
                
                # If one is pivot and one is variant, point to pivot
                if i != p_i and j == p_i:
                    src, dst = i, j
                elif j != p_j and i == p_j:
                    src, dst = j, i
                else:
                    # Mutual or same-status
                    src, dst = i, j
                    
                edges.append({
                    "from": src,
                    "to": dst,
                    "similarity": round(score, 4),
                    "label": f"{int(score * 100)}%"
                })
                
    return {
        "nodes": node_metadata,
        "edges": edges,
        "replacement_rules": replacement_rules,
        "pivot_count": len(pivot_set),
        "total_symbols": n
    }

def process_domain_file(filepath, domain_id, domain_title):
    print(f"\nProcessing domain: {domain_title} ({filepath})...")
    with open(filepath, "r", encoding="utf-8") as f:
        symbols = json.load(f)
        
    # Pre-clean symbols
    valid_symbols = []
    for s in symbols:
        if s.get("name") and s.get("notion"):
            valid_symbols.append({
                "name": s["name"].strip(),
                "type": s.get("type", "Object").strip(),
                "notion": s.get("notion", "").strip(),
                "impact": s.get("impact", "").strip()
            })
            
    print(f"  Valid symbols: {len(valid_symbols)}")
    
    # Compute embeddings
    name_texts = [s["name"] for s in valid_symbols]
    notion_texts = [f"{s['name']}: {s['notion']}" for s in valid_symbols]
    
    name_embs = get_embeddings(name_texts)
    notion_embs = get_embeddings(notion_texts)
    
    # Compute similarity
    sim_matrix = compute_similarity_matrix(valid_symbols, name_embs, notion_embs)
    
    # Run Pivot algorithm
    thesaurus = run_pivot_term_determination(valid_symbols, sim_matrix, threshold=0.68, top_k=5)
    thesaurus["domain_id"] = domain_id
    thesaurus["domain_title"] = domain_title
    
    print(f"  Pivots: {thesaurus['pivot_count']}, Replacement Rules: {len(thesaurus['replacement_rules'])}, Edges: {len(thesaurus['edges'])}")
    return thesaurus

def build_all_thesauri():
    os.makedirs("output", exist_ok=True)
    
    domains = [
        ("hospital", "Hospital Management (2025)", "domain/lel_hospital_2025.json"),
        ("military", "Military Academy Discipline (2025)", "domain/lel_military_2025.json"),
        ("genetic_lab", "Genetic Laboratory - Consolidated (2024)", "domain/lel_genetic_lab_2024.json"),
        ("ttps_g01", "Genetic Lab - TTPS Group 01", "domain/lel_ttps_group_01.json"),
        ("ttps_g01_2026", "Genetic Lab - TTPS Group 1 (2026)", "domain/lel_ttps_group_1_2026.json"),
        ("ttps_g02", "Genetic Lab - TTPS Group 02", "domain/lel_ttps_group_02.json"),
        ("ttps_g03", "Genetic Lab - TTPS Group 03", "domain/lel_ttps_group_03.json"),
        ("ttps_g04", "Genetic Lab - TTPS Group 04", "domain/lel_ttps_group_04.json"),
        ("tomato", "Tomato Cultivation (2024)", "domain/lel_tomato_2024.json"),
    ]
    
    thesauri_data = {}
    for dom_id, dom_title, dom_path in domains:
        if os.path.exists(dom_path):
            t_data = process_domain_file(dom_path, dom_id, dom_title)
            thesauri_data[dom_id] = t_data
            
    # Also build Cross-Domain / All Combined dataset
    print("\nBuilding Cross-Domain (All Combined) thesaurus...")
    combined_symbols = []
    for dom_id, dom_title, dom_path in domains:
        if dom_id in ["hospital", "military", "genetic_lab", "tomato"] and os.path.exists(dom_path):
            with open(dom_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    c_item = dict(item)
                    c_item["origin_domain"] = dom_title
                    combined_symbols.append(c_item)
                    
    name_texts = [s["name"] for s in combined_symbols]
    notion_texts = [f"{s['name']}: {s.get('notion','')}" for s in combined_symbols]
    name_embs = get_embeddings(name_texts)
    notion_embs = get_embeddings(notion_texts)
    sim_matrix = compute_similarity_matrix(combined_symbols, name_embs, notion_embs)
    comb_thesaurus = run_pivot_term_determination(combined_symbols, sim_matrix, threshold=0.68, top_k=5)
    comb_thesaurus["domain_id"] = "all_combined"
    comb_thesaurus["domain_title"] = "All Combined Domains (Cross-Evaluation)"
    thesauri_data["all_combined"] = comb_thesaurus
    
    out_json = "output/thesaurus_data.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(thesauri_data, f, indent=2, ensure_ascii=False)
    print(f"\nAll thesaurus data saved successfully to {out_json} ({os.path.getsize(out_json)} bytes)!")

if __name__ == "__main__":
    build_all_thesauri()

