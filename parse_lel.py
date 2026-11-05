import re
import json

with open(r'c:\Users\juane\Desktop\Glosario_LEL.md', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'### \*\*(Sujeto|Objeto|Verbo|Estado):\s*(.*?)\*\*'
splits = list(re.finditer(pattern, text))

def clean_text(s):
    # Remove markdown bold/italic
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    # Fix spaces before punctuation
    s = re.sub(r'\s+([,.:;])', r'\1', s)
    # Normalize multiple whitespace
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()

def clean_impact(s):
    lines = s.strip().split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r'^[-\*•]\s*', '', line)
        line = clean_text(line)
        if line:
            if not line.endswith('.'):
                line += '.'
            cleaned_lines.append(line)
    return ' '.join(cleaned_lines)

type_map = {
    'Sujeto': 'Subject',
    'Objeto': 'Object',
    'Verbo': 'Verb',
    'Estado': 'State'
}

entries_es = []
for idx, match in enumerate(splits):
    raw_type = match.group(1)
    name = match.group(2).strip()
    
    start = match.end()
    end = splits[idx+1].start() if idx+1 < len(splits) else len(text)
    section = text[start:end]
    
    notion_match = re.search(r'\*\*Noción:?\s*(.*?)(?:#{2,4}\s*\*\*Impacto|\*\*Impacto)', section, re.DOTALL | re.IGNORECASE)
    notion = clean_text(notion_match.group(1)) if notion_match else ''
    # strip leading colon if any
    notion = re.sub(r'^:\s*', '', notion)
    
    impact_match = re.search(r'(?:#{2,4}\s*\*\*Impacto:?\*\*|\*\*Impacto:?\*\*):?\s*(.*)', section, re.DOTALL | re.IGNORECASE)
    impact = clean_impact(impact_match.group(1)) if impact_match else ''
    
    entries_es.append({
        'name': name,
        'type': type_map.get(raw_type, raw_type),
        'notion': notion,
        'impact': impact
    })

print(f"Extracted {len(entries_es)} Spanish entries.")
with open('domain/lel_ttps_group_1_2026_es.json', 'w', encoding='utf-8') as f:
    json.dump(entries_es, f, indent=4, ensure_ascii=False)
print("Saved domain/lel_ttps_group_1_2026_es.json")

