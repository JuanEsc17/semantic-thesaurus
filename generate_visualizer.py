import json
import os

with open("output/thesaurus_data.json", "r", encoding="utf-8") as f:
    thesaurus_data = json.load(f)

json_str = json.dumps(thesaurus_data, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Semantic Thesaurus Explorer & Visualizer</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {{
      --bg-dark: #0f172a;
      --bg-card: #1e293b;
      --bg-card-hover: #334155;
      --border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.25);
      --subject-color: #3b82f6;
      --object-color: #10b981;
      --verb-color: #f59e0b;
      --state-color: #a855f7;
      --pivot-color: #fbbf24;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    body {{
      background: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    /* Header */
    header {{
      background: #111827;
      border-bottom: 1px solid var(--border);
      padding: 10px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 15px;
      z-index: 20;
    }}
    .logo-area {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-icon {{
      background: linear-gradient(135deg, #0ea5e9, #6366f1);
      width: 38px;
      height: 38px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }}
    .logo-title h1 {{
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.3px;
    }}
    .logo-title p {{
      font-size: 11px;
      color: var(--text-muted);
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    select, input, button {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 7px 12px;
      border-radius: 6px;
      font-size: 13px;
      outline: none;
      transition: all 0.15s ease;
    }}
    select:focus, input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-glow);
    }}
    button {{
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-weight: 500;
    }}
    button:hover {{
      background: var(--bg-card-hover);
      border-color: #475569;
    }}
    button.primary {{
      background: #0284c7;
      border-color: #0369a1;
    }}
    button.primary:hover {{
      background: #0369a1;
    }}
    /* Tabs Bar */
    .tab-bar {{
      display: flex;
      background: #0b0f19;
      border-bottom: 1px solid var(--border);
      padding: 0 20px;
    }}
    .tab-btn {{
      background: transparent;
      border: none;
      border-radius: 0;
      padding: 10px 18px;
      color: var(--text-muted);
      border-bottom: 2px solid transparent;
      font-size: 13px;
    }}
    .tab-btn:hover {{
      color: var(--text-main);
      background: transparent;
    }}
    .tab-btn.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
      background: rgba(56, 189, 248, 0.05);
    }}
    /* Main Layout */
    .main-container {{
      flex: 1;
      display: flex;
      position: relative;
      overflow: hidden;
    }}
    /* Left / Center Viewports */
    .viewport {{
      flex: 1;
      height: 100%;
      position: relative;
      display: none;
    }}
    .viewport.active {{
      display: flex;
      flex-direction: column;
    }}
    #network-canvas {{
      flex: 1;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
    }}
    /* Floating Graph Overlay Controls */
    .graph-overlay-top {{
      position: absolute;
      top: 15px;
      left: 20px;
      z-index: 10;
      display: flex;
      gap: 10px;
      align-items: center;
      background: rgba(15, 23, 42, 0.88);
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      backdrop-filter: blur(8px);
    }}
    .legend-bar {{
      position: absolute;
      bottom: 20px;
      left: 20px;
      z-index: 10;
      background: rgba(15, 23, 42, 0.88);
      padding: 10px 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
      backdrop-filter: blur(8px);
      display: flex;
      gap: 16px;
      font-size: 12px;
      align-items: center;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }}
    /* Sidebar Details Panel */
    .sidebar {{
      width: 380px;
      background: #111827;
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow-y: auto;
      z-index: 15;
      transition: all 0.2s ease;
    }}
    .sidebar-header {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .sidebar-header h2 {{
      font-size: 15px;
      font-weight: 600;
    }}
    .sidebar-body {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      font-size: 13px;
      line-height: 1.5;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .badge-subject {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }}
    .badge-object  {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .badge-verb    {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
    .badge-state   {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .badge-pivot   {{ background: rgba(251, 191, 36, 0.2); color: #fde047; border: 1px solid rgba(251, 191, 36, 0.5); }}
    
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
    }}
    .card-title {{
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-bottom: 8px;
      letter-spacing: 0.5px;
    }}
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}
    .metric-box {{
      background: #0f172a;
      padding: 8px 10px;
      border-radius: 6px;
      text-align: center;
    }}
    .metric-val {{
      font-size: 16px;
      font-weight: 700;
      color: var(--accent);
    }}
    .metric-lbl {{
      font-size: 10px;
      color: var(--text-muted);
      margin-top: 2px;
    }}
    .synonym-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #0f172a;
      border: 1px solid #334155;
      padding: 4px 10px;
      border-radius: 14px;
      margin: 3px 4px 3px 0;
      font-size: 12px;
      cursor: pointer;
    }}
    .synonym-chip:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}
    .table-container {{
      flex: 1;
      padding: 24px;
      overflow-y: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 12px 14px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      background: #111827;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.5px;
      position: sticky;
      top: 0;
    }}
    tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}
    .tree-view {{
      padding: 24px;
      overflow-y: auto;
      max-width: 900px;
      margin: 0 auto;
      width: 100%;
    }}
    .tree-node {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 14px;
      padding: 16px;
    }}
    .tree-node-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
  </style>
</head>
<body>

  <!-- Top Header -->
  <header>
    <div class="logo-area">
      <div class="logo-icon"><i class="fa-solid fa-diagram-project"></i></div>
      <div class="logo-title">
        <h1>Semantic Thesaurus Explorer</h1>
        <p>NLP-Powered Domain Thesaurus & Pivot Term Determination (Moon et al., 2022)</p>
      </div>
    </div>
    
    <div class="header-controls">
      <label style="font-size:12px; color:var(--text-muted);">Domain:</label>
      <select id="domainSelect" onchange="changeDomain()">
        <option value="hospital">Hospital Management (2025)</option>
        <option value="military">Military Academy Discipline (2025)</option>
        <option value="genetic_lab">Genetic Laboratory (Consolidated 2024)</option>
        <option value="ttps_g01">Genetic Lab - Group 01</option>
        <option value="ttps_g02">Genetic Lab - Group 02</option>
        <option value="ttps_g03">Genetic Lab - Group 03</option>
        <option value="ttps_g04">Genetic Lab - Group 04</option>
        <option value="all_combined">All Combined Domains (Cross-Review)</option>
      </select>
      
      <div style="position:relative;">
        <input type="text" id="searchInput" placeholder="Search symbol or synonym..." onkeyup="searchSymbol(event)" style="width:220px; padding-left:28px;">
        <i class="fa-solid fa-magnifying-glass" style="position:absolute; left:9px; top:10px; color:#64748b; font-size:12px;"></i>
      </div>
      
      <button onclick="exportJSON()"><i class="fa-solid fa-download"></i> JSON</button>
      <button onclick="exportCSV()"><i class="fa-solid fa-file-csv"></i> Rules CSV</button>
    </div>
  </header>

  <!-- Navigation Tab Bar -->
  <div class="tab-bar">
    <button class="tab-btn active" onclick="switchTab('graph')"><i class="fa-solid fa-circle-nodes"></i> Interactive Graph</button>
    <button class="tab-btn" onclick="switchTab('table')"><i class="fa-solid fa-table-list"></i> Replacement Rules (Paper Table 6)</button>
    <button class="tab-btn" onclick="switchTab('skos')"><i class="fa-solid fa-sitemap"></i> SKOS Concept Tree</button>
    <button class="tab-btn" onclick="switchTab('algorithm')"><i class="fa-solid fa-brain"></i> Paper Algorithm & Formulas</button>
  </div>

  <!-- Main View Area -->
  <div class="main-container">
    
    <!-- View 1: Interactive Network Graph -->
    <div id="view-graph" class="viewport active">
      <div class="graph-overlay-top">
        <label style="font-size:12px; color:var(--text-muted);"><i class="fa-solid fa-filter"></i> Type:</label>
        <label><input type="checkbox" id="filter-Subject" checked onchange="applyFilters()"> Subject</label>
        <label><input type="checkbox" id="filter-Object" checked onchange="applyFilters()"> Object</label>
        <label><input type="checkbox" id="filter-Verb" checked onchange="applyFilters()"> Verb</label>
        <label><input type="checkbox" id="filter-State" checked onchange="applyFilters()"> State</label>
        
        <span style="border-left:1px solid var(--border); height:16px; margin:0 4px;"></span>
        <label><input type="checkbox" id="filter-only-connected" checked onchange="applyFilters()"> Only Synonyms</label>
        
        <span style="border-left:1px solid var(--border); height:16px; margin:0 4px;"></span>
        <button onclick="togglePhysics()"><i class="fa-solid fa-atom"></i> <span id="physicsBtnText">Freeze Layout</span></button>
        <button onclick="network.fit()"><i class="fa-solid fa-expand"></i> Reset View</button>
      </div>

      <div id="network-canvas"></div>

      <!-- Legend -->
      <div class="legend-bar">
        <span style="font-weight:600; color:var(--text-muted); text-transform:uppercase; font-size:10px;">LEL Types:</span>
        <div class="legend-item"><div class="legend-dot" style="background:#3b82f6;"></div> Subject</div>
        <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> Object</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div> Verb</div>
        <div class="legend-item"><div class="legend-dot" style="background:#a855f7;"></div> State</div>
        <span style="border-left:1px solid var(--border); height:14px; margin:0 4px;"></span>
        <div class="legend-item"><i class="fa-solid fa-crown" style="color:#fbbf24;"></i> Pivot Term (Gold Ring)</div>
        <div class="legend-item"><i class="fa-solid fa-arrow-right" style="color:#94a3b8;"></i> USE (Points to Pivot)</div>
      </div>
    </div>

    <!-- View 2: Replacement Rules Table -->
    <div id="view-table" class="viewport">
      <div class="table-container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h2 style="font-size:18px;">Automated Word-Replacement Rules</h2>
          <p style="font-size:13px; color:var(--text-muted);" id="tableSummary">Showing rules where a non-pivot term is mapped to its canonical Pivot Term.</p>
        </div>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Target Term (Variant)</th>
              <th>Type</th>
              <th>Direction</th>
              <th>Pivot Term (Canonical)</th>
              <th>Similarity</th>
              <th>Target Margin ($f_w$)</th>
              <th>Pivot Margin ($f_w$)</th>
            </tr>
          </thead>
          <tbody id="rulesTableBody"></tbody>
        </table>
      </div>
    </div>

    <!-- View 3: SKOS Concept Tree -->
    <div id="view-skos" class="viewport">
      <div class="tree-view" id="skosContainer"></div>
    </div>

    <!-- View 4: Paper Algorithm & Formulas -->
    <div id="view-algorithm" class="viewport" style="padding:30px; overflow-y:auto;">
      <div style="max-width:850px; margin:0 auto; background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:24px;">
        <h2 style="margin-bottom:12px; color:var(--accent);">Semantic Thesaurus Construction & Pivot Determination</h2>
        <p style="margin-bottom:16px; color:var(--text-muted); font-size:14px;">Based on <em>Moon, Lee & Chi (2022) - "Automated system for construction specification review using NLP" (Advanced Engineering Informatics)</em>.</p>
        
        <h3 style="margin:20px 0 8px 0; font-size:15px; color:#f8fafc;">1. The Recursive Loop Problem</h3>
        <p style="font-size:13px; line-height:1.6; color:#cbd5e1;">In natural language domain corpora, synonym detection algorithms easily fall into recursive loops: word $A$ is similar to $B$, $B$ is similar to $C$, and $C$ points back to $A$ (e.g. <code>Doctor</code> &harr; <code>Physician</code> &harr; <code>Medical Specialist</code>). Which term should be standardized as the canonical descriptor?</p>
        
        <h3 style="margin:20px 0 8px 0; font-size:15px; color:#f8fafc;">2. The PivotTermDetermination Algorithm (PageRank-Inspired)</h3>
        <p style="font-size:13px; line-height:1.6; color:#cbd5e1;">The authors formulated the concepts of <strong>Inflow</strong> and <strong>Outflow</strong> based on directional similarities:</p>
        
        <div style="background:#0f172a; padding:16px; border-radius:8px; margin:14px 0; font-family:monospace; font-size:13px; line-height:1.8;">
          <strong>(1) Rank Weight:</strong> g(w', W) = ( n(W) - index(w'|sorted(W)) ) / n(W)<br>
          <strong>(2) Inflow:</strong> inflow_w = &sum; g(w', W_out(w')) &times; c(w, w')<br>
          <strong>(3) Outflow:</strong> outflow_w = &sum; g(w', W_out(w)) &times; c(w, w')<br>
          <strong>(4) Flow Margin:</strong> f_w = inflow_w - outflow_w
        </div>
        
        <h3 style="margin:20px 0 8px 0; font-size:15px; color:#f8fafc;">3. Decision Rules</h3>
        <ul style="font-size:13px; line-height:1.8; color:#cbd5e1; margin-left:20px;">
          <li>If $f_w > 0$: The term has positive incoming authority &rarr; <strong>Keep as Pivot Term (Preferred Descriptor)</strong>.</li>
          <li>If $f_w \le 0$: Replace with the most similar word whose flow margin is positive: <code>Target &rarr; USE &rarr; Pivot</code>.</li>
        </ul>
      </div>
    </div>

    <!-- Right Sidebar Inspector -->
    <div class="sidebar" id="nodeSidebar">
      <div class="sidebar-header">
        <h2><i class="fa-solid fa-circle-info" style="color:var(--accent);"></i> Symbol Inspector</h2>
        <span id="sideBadgeType" class="badge">SUBJECT</span>
      </div>
      <div class="sidebar-body" id="sideContent">
        <p style="color:var(--text-muted); text-align:center; padding-top:40px;">Select any node in the graph or table to view its semantic properties, LEL notion, and thesaurus relationships.</p>
      </div>
    </div>

  </div>

  <!-- Embedded Thesaurus Data -->
  <script type="text/javascript">
    const THESAURUS_DB = {json_str};
    let currentDomain = "hospital";
    let network = null;
    let nodesDataSet = null;
    let edgesDataSet = null;
    let isPhysicsActive = true;

    const TYPE_COLORS = {{
      "Subject": {{ bg: "#3b82f6", border: "#2563eb", highlight: "#60a5fa" }},
      "Object":  {{ bg: "#10b981", border: "#059669", highlight: "#34d399" }},
      "Verb":    {{ bg: "#f59e0b", border: "#d97706", highlight: "#fbbf24" }},
      "State":   {{ bg: "#a855f7", border: "#7e22ce", highlight: "#c084fc" }}
    }};

    function init() {{
      renderDomain(currentDomain);
    }}

    function changeDomain() {{
      const select = document.getElementById("domainSelect");
      currentDomain = select.value;
      renderDomain(currentDomain);
    }}

    function renderDomain(domKey) {{
      const data = THESAURUS_DB[domKey];
      if (!data) return;

      renderGraph(data);
      renderTable(data);
      renderSKOS(data);
    }}

    function renderGraph(data) {{
      const container = document.getElementById("network-canvas");
      
      const filterSubject = document.getElementById("filter-Subject").checked;
      const filterObject = document.getElementById("filter-Object").checked;
      const filterVerb = document.getElementById("filter-Verb").checked;
      const filterState = document.getElementById("filter-State").checked;
      const onlyConnected = document.getElementById("filter-only-connected").checked;

      const allowedTypes = new Set();
      if (filterSubject) allowedTypes.add("Subject");
      if (filterObject) allowedTypes.add("Object");
      if (filterVerb) allowedTypes.add("Verb");
      if (filterState) allowedTypes.add("State");

      const visNodes = [];
      const nodeMap = new Map();

      data.nodes.forEach(n => {{
        if (!allowedTypes.has(n.type)) return;
        if (onlyConnected && !n.has_connections) return;

        const colorCfg = TYPE_COLORS[n.type] || TYPE_COLORS["Object"];
        
        let label = n.name;
        if (n.is_pivot) {{
          label = "👑 " + n.name;
        }}

        const nodeObj = {{
          id: n.id,
          label: label,
          shape: n.is_pivot ? "box" : "dot",
          size: n.is_pivot ? 32 : 18,
          font: {{
            color: "#ffffff",
            size: n.is_pivot ? 14 : 12,
            face: "Segoe UI, sans-serif",
            bold: n.is_pivot ? "bold" : "normal"
          }},
          color: {{
            background: colorCfg.bg,
            border: n.is_pivot ? "#fbbf24" : colorCfg.border,
            highlight: {{
              background: colorCfg.highlight,
              border: "#fbbf24"
            }}
          }},
          borderWidth: n.is_pivot ? 3 : 1,
          shadow: n.is_pivot ? {{ enabled: true, color: "rgba(251, 191, 36, 0.4)", size: 10 }} : false,
          margin: 10,
          raw: n
        }};

        visNodes.push(nodeObj);
        nodeMap.set(n.id, nodeObj);
      }});

      const visEdges = [];
      data.edges.forEach((e, idx) => {{
        if (nodeMap.has(e.from) && nodeMap.has(e.to)) {{
          visEdges.push({{
            id: "e_" + idx,
            from: e.from,
            to: e.to,
            arrows: "to",
            label: e.label,
            font: {{ color: "#94a3b8", size: 10, align: "middle", background: "#0f172a" }},
            color: {{ color: "rgba(148, 163, 184, 0.6)", highlight: "#38bdf8" }},
            width: 1.5 + (e.similarity - 0.6) * 4,
            smooth: {{ type: "continuous" }}
          }});
        }}
      }});

      nodesDataSet = new vis.DataSet(visNodes);
      edgesDataSet = new vis.DataSet(visEdges);

      const options = {{
        physics: {{
          enabled: isPhysicsActive,
          solver: "forceAtlas2Based",
          forceAtlas2Based: {{
            gravitationalConstant: -70,
            centralGravity: 0.015,
            springLength: 140,
            springConstant: 0.08
          }},
          stabilization: {{ iterations: 150 }}
        }},
        interaction: {{
          hover: true,
          tooltipDelay: 200,
          zoomView: true
        }}
      }};

      network = new vis.Network(container, {{ nodes: nodesDataSet, edges: edgesDataSet }}, options);

      network.on("click", function(params) {{
        if (params.nodes.length > 0) {{
          const clickedId = params.nodes[0];
          const nodeData = nodeMap.get(clickedId).raw;
          inspectNode(nodeData);
        }}
      }});
    }}

    function inspectNode(node) {{
      const sideBadge = document.getElementById("sideBadgeType");
      sideBadge.className = "badge badge-" + node.type.toLowerCase();
      sideBadge.innerText = node.type;

      const sideContent = document.getElementById("sideContent");
      
      let statusHtml = "";
      if (node.is_pivot) {{
        statusHtml = `<div class="card" style="border-color:#f59e0b; background:rgba(245, 158, 11, 0.08);">
          <div style="font-weight:700; color:#fbbf24; font-size:14px; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-crown"></i> Pivot Term (Preferred Descriptor)
          </div>
          <div style="font-size:12px; color:#cbd5e1; margin-top:4px;">
            Standardized canonical term for this synonym cluster.
          </div>
        </div>`;
      }} else if (node.has_connections) {{
        statusHtml = `<div class="card" style="border-color:#38bdf8; background:rgba(56, 189, 248, 0.08);">
          <div class="card-title">Thesaurus Equivalence (USE)</div>
          <div style="font-size:13px; color:#f8fafc;">
            Non-preferred variant. Replace with:
          </div>
          <button class="primary" style="margin-top:8px; width:100%; justify-content:center;" onclick="focusNode(${{node.pivot_id}})">
            <i class="fa-solid fa-arrow-right"></i> USE: ${{node.pivot_name}}
          </button>
        </div>`;
      }} else {{
        statusHtml = `<div class="card">
          <div style="font-size:12px; color:var(--text-muted);">
            Isolated term (No synonym above threshold in current domain).
          </div>
        </div>`;
      }}

      let synonymsHtml = "";
      if (node.is_pivot && node.used_for && node.used_for.length > 0) {{
        synonymsHtml = `<div class="card">
          <div class="card-title">Used For (UF / Synonyms)</div>
          <div>
            ${{node.used_for.map(u => `<span class="synonym-chip"><i class="fa-solid fa-tag" style="font-size:10px;"></i> ${{u.name}} <strong style="color:var(--accent); font-size:10px;">${{Math.round(u.similarity*100)}}%</strong></span>`).join("")}}
          </div>
        </div>`;
      }}

      sideContent.innerHTML = `
        <h1 style="font-size:20px; font-weight:700;">${{node.name}}</h1>
        ${{statusHtml}}

        <div class="card">
          <div class="card-title">Pivot Determination Metrics (Paper Eq. 1-4)</div>
          <div class="metrics-grid">
            <div class="metric-box">
              <div class="metric-val" style="color:#10b981;">+${{node.inflow.toFixed(2)}}</div>
              <div class="metric-lbl">Inflow</div>
            </div>
            <div class="metric-box">
              <div class="metric-val" style="color:#ef4444;">-${{node.outflow.toFixed(2)}}</div>
              <div class="metric-lbl">Outflow</div>
            </div>
            <div class="metric-box">
              <div class="metric-val" style="color:${{node.flow_margin >= 0 ? '#fbbf24' : '#94a3b8'}};">${{node.flow_margin >= 0 ? '+' : ''}}${{node.flow_margin.toFixed(2)}}</div>
              <div class="metric-lbl">Flow Margin ($f_w$)</div>
            </div>
          </div>
        </div>

        ${{synonymsHtml}}

        <div class="card">
          <div class="card-title">LEL Notion (Formal Concept Definition)</div>
          <p style="font-size:12px; color:#e2e8f0; line-height:1.6;">${{node.notion || "N/A"}}</p>
        </div>

        <div class="card">
          <div class="card-title">LEL Impact (Contextual Usage / Behavior)</div>
          <p style="font-size:12px; color:#cbd5e1; line-height:1.6;">${{node.impact || "N/A"}}</p>
        </div>
      `;
    }}

    function focusNode(nodeId) {{
      if (!network || !nodesDataSet) return;
      network.focus(nodeId, {{
        scale: 1.2,
        animation: {{ duration: 600, easingFunction: "easeInOutQuad" }}
      }});
      network.selectNodes([nodeId]);
      const data = THESAURUS_DB[currentDomain];
      const target = data.nodes.find(x => x.id === nodeId);
      if (target) inspectNode(target);
    }}

    function applyFilters() {{
      const data = THESAURUS_DB[currentDomain];
      if (data) renderGraph(data);
    }}

    function togglePhysics() {{
      isPhysicsActive = !isPhysicsActive;
      network.setOptions({{ physics: {{ enabled: isPhysicsActive }} }});
      document.getElementById("physicsBtnText").innerText = isPhysicsActive ? "Freeze Layout" : "Unfreeze Layout";
    }}

    function searchSymbol(event) {{
      const q = event.target.value.toLowerCase().trim();
      if (!q || !network) return;
      
      const data = THESAURUS_DB[currentDomain];
      const match = data.nodes.find(n => n.name.toLowerCase().includes(q));
      if (match) {{
        focusNode(match.id);
      }}
    }}

    function switchTab(tabKey) {{
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".viewport").forEach(v => v.classList.remove("active"));

      const targetTab = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick").includes(tabKey));
      if (targetTab) targetTab.classList.add("active");

      const targetView = document.getElementById("view-" + tabKey);
      if (targetView) targetView.classList.add("active");
    }}

    function renderTable(data) {{
      const tbody = document.getElementById("rulesTableBody");
      const rules = data.replacement_rules || [];
      document.getElementById("tableSummary").innerText = `Total of ${{rules.length}} word-replacement rules identified for ${{data.domain_title}}.`;
      
      tbody.innerHTML = rules.map((r, i) => `
        <tr>
          <td>${{i + 1}}</td>
          <td><strong style="color:#f8fafc;">${{r.target_name}}</strong></td>
          <td><span class="badge badge-${{r.target_type.toLowerCase()}}">${{r.target_type}}</span></td>
          <td style="color:#38bdf8;"><i class="fa-solid fa-arrow-right"></i> USE</td>
          <td><strong style="color:#fbbf24;"><i class="fa-solid fa-crown" style="font-size:10px;"></i> ${{r.pivot_name}}</strong></td>
          <td><span style="background:rgba(56, 189, 248, 0.15); color:#38bdf8; padding:3px 7px; border-radius:4px; font-weight:600;">${{Math.round(r.similarity * 100)}}%</span></td>
          <td style="color:#ef4444;">${{r.target_margin.toFixed(2)}}</td>
          <td style="color:#10b981;">+${{r.pivot_margin.toFixed(2)}}</td>
        </tr>
      `).join("");
    }}

    function renderSKOS(data) {{
      const container = document.getElementById("skosContainer");
      const pivots = data.nodes.filter(n => n.is_pivot);

      container.innerHTML = `
        <div style="margin-bottom:20px;">
          <h2 style="font-size:18px;">SKOS Canonical Concepts (Thesaurus Taxonomy)</h2>
          <p style="font-size:13px; color:var(--text-muted);">Each concept represents a standardized Pivot Term (skos:prefLabel) and its mapped synonyms (skos:altLabel).</p>
        </div>
        ${{pivots.map(p => `
          <div class="tree-node">
            <div class="tree-node-header">
              <div style="display:flex; align-items:center; gap:10px;">
                <i class="fa-solid fa-crown" style="color:#fbbf24; font-size:16px;"></i>
                <h3 style="font-size:16px; font-weight:700; color:#f8fafc;">${{p.name}}</h3>
                <span class="badge badge-${{p.type.toLowerCase()}}">${{p.type}}</span>
              </div>
              <span class="badge badge-pivot">skos:Concept</span>
            </div>
            
            <div style="margin:10px 0; font-size:13px; color:#cbd5e1;">
              <strong>skos:definition:</strong> ${{p.notion}}
            </div>

            ${{p.used_for && p.used_for.length > 0 ? `
              <div style="margin-top:12px; padding-top:10px; border-top:1px solid var(--border);">
                <span style="font-size:11px; font-weight:600; color:var(--text-muted); text-transform:uppercase;">skos:altLabel (Synonyms / UF):</span>
                <div style="margin-top:6px;">
                  ${{p.used_for.map(u => `<span class="synonym-chip">${{u.name}} <strong style="color:var(--accent); font-size:10px;">${{Math.round(u.similarity*100)}}%</strong></span>`).join("")}}
                </div>
              </div>
            ` : ''}}
          </div>
        `).join("")}}
      `;
    }}

    function exportJSON() {{
      const data = THESAURUS_DB[currentDomain];
      const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: "application/json" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `thesaurus_${{currentDomain}}.json`;
      a.click();
    }}

    function exportCSV() {{
      const data = THESAURUS_DB[currentDomain];
      const rules = data.replacement_rules || [];
      let csv = "Index,Target_Term,Target_Type,Relation,Pivot_Term,Pivot_Type,Similarity,Target_Margin,Pivot_Margin\\n";
      rules.forEach((r, i) => {{
        csv += `${{i+1}},"${{r.target_name}}",${{r.target_type}},USE,"${{r.pivot_name}}",${{r.pivot_type}},${{r.similarity}},${{r.target_margin}},${{r.pivot_margin}}\\n`;
      }});
      const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `replacement_rules_${{currentDomain}}.csv`;
      a.click();
    }}

    window.onload = init;
  </script>
</body>
</html>
"""

out_html = "thesaurus_visualizer.html"
with open(out_html, "w", encoding="utf-8") as f:
    f.write(html_content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Interactive visualizer generated: {out_html} and index.html ({os.path.getsize(out_html)} bytes)")

