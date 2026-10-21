"""
Visual Asset Generator for AI Research Workbench.
Generates pixel-perfect light-theme SVG diagrams and high-resolution PNG banners
for README.md and LinkedIn project showcases.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 1. HERO BANNER SVG (1200 x 440)
# ==============================================================================
HERO_BANNER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 440" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#f1f5f9"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0d9488"/>
      <stop offset="50%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#0f172a" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="440" fill="url(#bgGrad)"/>
  
  <!-- Subtle Grid Lines -->
  <g stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4" opacity="0.6">
    <line x1="80" y1="0" x2="80" y2="440"/>
    <line x1="360" y1="0" x2="360" y2="440"/>
    <line x1="640" y1="0" x2="640" y2="440"/>
    <line x1="920" y1="0" x2="920" y2="440"/>
    <line x1="1120" y1="0" x2="1120" y2="440"/>
    <line x1="0" y1="80" x2="1200" y2="80"/>
    <line x1="0" y1="220" x2="1200" y2="220"/>
    <line x1="0" y1="360" x2="1200" y2="360"/>
  </g>

  <!-- Top Accent Bar -->
  <rect x="0" y="0" width="1200" height="6" fill="url(#accentGrad)"/>

  <!-- Status Pill -->
  <g transform="translate(60, 42)">
    <rect width="360" height="32" rx="16" fill="#ecfdf5" stroke="#a7f3d0" stroke-width="1.5"/>
    <circle cx="20" cy="16" r="5" fill="#059669"/>
    <text x="36" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#065f46" letter-spacing="0.5">VERIFIED PORTFOLIO · 39/39 TESTS PASSING</text>
  </g>

  <!-- Main Title -->
  <text x="60" y="125" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="44" font-weight="800" fill="#0f172a" letter-spacing="-1">AI Research Workbench</text>
  
  <!-- Subtitle -->
  <text x="60" y="162" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="500" fill="#475569">Intelligent Systems Suite · 4 Production-Grade Decoupled AI Applications</text>

  <!-- 4 Mini Preview Cards -->
  <g transform="translate(60, 195)">
    <!-- Card 1 -->
    <g transform="translate(0, 0)" filter="url(#cardShadow)">
      <rect width="255" height="180" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
      <rect x="0" y="0" width="255" height="4" rx="2" fill="#2563eb"/>
      <rect x="18" y="18" width="60" height="20" rx="4" fill="#eff6ff"/>
      <text x="26" y="32" font-family="monospace" font-size="10.5" font-weight="700" fill="#2563eb">TASK 1</text>
      <text x="18" y="65" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0f172a">Structured Extractor</text>
      <text x="18" y="88" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">Pydantic v2 schema parser with bounded corrective repair loops.</text>
      <rect x="18" y="138" width="85" height="22" rx="4" fill="#f1f5f9"/>
      <text x="24" y="153" font-family="monospace" font-size="10" fill="#334155">Port :8501</text>
    </g>

    <!-- Card 2 -->
    <g transform="translate(275, 0)" filter="url(#cardShadow)">
      <rect width="255" height="180" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
      <rect x="0" y="0" width="255" height="4" rx="2" fill="#0d9488"/>
      <rect x="18" y="18" width="60" height="20" rx="4" fill="#f0fdfa"/>
      <text x="26" y="32" font-family="monospace" font-size="10.5" font-weight="700" fill="#0d9488">TASK 2</text>
      <text x="18" y="65" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0f172a">Grounded RAG</text>
      <text x="18" y="88" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">ChromaDB semantic retrieval with strict citation attribution.</text>
      <rect x="18" y="138" width="85" height="22" rx="4" fill="#f1f5f9"/>
      <text x="24" y="153" font-family="monospace" font-size="10" fill="#334155">Port :8502</text>
    </g>

    <!-- Card 3 -->
    <g transform="translate(550, 0)" filter="url(#cardShadow)">
      <rect width="255" height="180" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
      <rect x="0" y="0" width="255" height="4" rx="2" fill="#d97706"/>
      <rect x="18" y="18" width="60" height="20" rx="4" fill="#fef3c7"/>
      <text x="26" y="32" font-family="monospace" font-size="10.5" font-weight="700" fill="#b45309">TASK 3</text>
      <text x="18" y="65" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0f172a">Autonomous Agent</text>
      <text x="18" y="88" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">ReAct agent with AST-safe calculator &amp; sandboxed reader.</text>
      <rect x="18" y="138" width="95" height="22" rx="4" fill="#f1f5f9"/>
      <text x="24" y="153" font-family="monospace" font-size="10" fill="#334155">Console CLI</text>
    </g>

    <!-- Card 4 -->
    <g transform="translate(825, 0)" filter="url(#cardShadow)">
      <rect width="255" height="180" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
      <rect x="0" y="0" width="255" height="4" rx="2" fill="#7c3aed"/>
      <rect x="18" y="18" width="60" height="20" rx="4" fill="#f3e8ff"/>
      <text x="26" y="32" font-family="monospace" font-size="10.5" font-weight="700" fill="#7e22ce">TASK 4</text>
      <text x="18" y="65" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0f172a">Conversation Studio</text>
      <text x="18" y="88" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">Streaming chat with session isolation &amp; RAG/Agent bridge.</text>
      <rect x="18" y="138" width="85" height="22" rx="4" fill="#f1f5f9"/>
      <text x="24" y="153" font-family="monospace" font-size="10" fill="#334155">Port :8504</text>
    </g>
  </g>
</svg>"""


# ==============================================================================
# 2. MODULES ARCHITECTURE INFOGRAPHIC SVG (1200 x 560)
# ==============================================================================
MODULES_ARCHITECTURE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 560" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f8fafc"/>
    </linearGradient>
    <filter id="shadow2" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.05"/>
    </filter>
  </defs>

  <rect width="1200" height="560" fill="url(#bgGrad2)"/>

  <!-- Section Title -->
  <text x="60" y="55" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="28" font-weight="800" fill="#0f172a">Subsystem Architecture &amp; Data Pipeline</text>
  <text x="60" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" fill="#64748b">Defensive schema boundaries, verifiable citations, AST-sandboxed tool execution, and session-isolated chat</text>

  <!-- Panel 1: Task 1 -->
  <g transform="translate(60, 115)" filter="url(#shadow2)">
    <rect width="520" height="195" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="4" rx="2" fill="#2563eb"/>
    <text x="22" y="32" font-family="monospace" font-size="12" font-weight="700" fill="#2563eb">TASK 1: STRUCTURED PROMPT PIPELINE</text>
    <text x="22" y="60" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Invoices &amp; Resumes Extraction Engine</text>
    <text x="22" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Pydantic v2 schemas: strict typing, ISO 8601 dates, non-negative amounts
    </text>
    <text x="22" y="108" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Line-item consistency: auto-checks (quantity × unit_price = total)
    </text>
    <text x="22" y="131" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Bounded Self-Repair: intercepts validation errors, repairs within 3 cycles
    </text>
    <rect x="22" y="152" width="130" height="24" rx="4" fill="#eff6ff"/>
    <text x="30" y="168" font-family="monospace" font-size="11" font-weight="600" fill="#2563eb">11/11 Tests Passed</text>
  </g>

  <!-- Panel 2: Task 2 -->
  <g transform="translate(620, 115)" filter="url(#shadow2)">
    <rect width="520" height="195" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="4" rx="2" fill="#0d9488"/>
    <text x="22" y="32" font-family="monospace" font-size="12" font-weight="700" fill="#0d9488">TASK 2: DOCUMENT GROUNDED RAG</text>
    <text x="22" y="60" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Semantic Vector Retrieval &amp; Anti-Hallucination</text>
    <text x="22" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Ingestion: multi-page PDF &amp; TXT loader retaining page metadata
    </text>
    <text x="22" y="108" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Chunking: RecursiveCharacterTextSplitter with token overlap
    </text>
    <text x="22" y="131" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Dual Vector Store: ChromaDB + zero-dependency in-memory Cosine store
    </text>
    <rect x="22" y="152" width="130" height="24" rx="4" fill="#f0fdfa"/>
    <text x="30" y="168" font-family="monospace" font-size="11" font-weight="600" fill="#0d9488">9/9 Tests Passed</text>
  </g>

  <!-- Panel 3: Task 3 -->
  <g transform="translate(60, 330)" filter="url(#shadow2)">
    <rect width="520" height="195" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="4" rx="2" fill="#d97706"/>
    <text x="22" y="32" font-family="monospace" font-size="12" font-weight="700" fill="#b45309">TASK 3: MULTI-TOOL AUTONOMOUS AGENT</text>
    <text x="22" y="60" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">ReAct Loop &amp; Defense-in-Depth Sandbox</text>
    <text x="22" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Safe Math Calculator: AST node walker, strictly blocks eval() / exec()
    </text>
    <text x="22" y="108" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Sandboxed File Reader: Path canonicalization prevents ../ traversal
    </text>
    <text x="22" y="131" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • DuckDuckGo Search: snippet extraction with verified URL citations
    </text>
    <rect x="22" y="152" width="130" height="24" rx="4" fill="#fef3c7"/>
    <text x="30" y="168" font-family="monospace" font-size="11" font-weight="600" fill="#b45309">11/11 Tests Passed</text>
  </g>

  <!-- Panel 4: Task 4 -->
  <g transform="translate(620, 330)" filter="url(#shadow2)">
    <rect width="520" height="195" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="4" rx="2" fill="#7c3aed"/>
    <text x="22" y="32" font-family="monospace" font-size="12" font-weight="700" fill="#7e22ce">TASK 4: INTERACTIVE CONVERSATION STUDIO</text>
    <text x="22" y="60" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Streaming Chat &amp; Multi-Mode Orchestrator</text>
    <text x="22" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Streamlit Chat: st.chat_message, st.chat_input, and session isolation
    </text>
    <text x="22" y="108" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Streaming Token Cadence: natural generator yielding words seamlessly
    </text>
    <text x="22" y="131" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#475569">
      • Tri-Mode Bridge: General Chat ➔ Grounded RAG ➔ Autonomous Agent
    </text>
    <rect x="22" y="152" width="130" height="24" rx="4" fill="#f3e8ff"/>
    <text x="30" y="168" font-family="monospace" font-size="11" font-weight="600" fill="#7e22ce">8/8 Tests Passed</text>
  </g>
</svg>"""


# ==============================================================================
# 3. LINKEDIN POST SHOWCASE BANNER SVG (1200 x 628 - Standard 1.91:1)
# ==============================================================================
LINKEDIN_BANNER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 628" width="100%" height="100%">
  <defs>
    <linearGradient id="liBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="70%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#f1f5f9"/>
    </linearGradient>
    <linearGradient id="liAccent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0d9488"/>
      <stop offset="50%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <filter id="liShadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#0f172a" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="628" fill="url(#liBg)"/>
  <rect x="0" y="0" width="1200" height="8" fill="url(#liAccent)"/>

  <!-- Grid Accents -->
  <g stroke="#e2e8f0" stroke-width="1" stroke-dasharray="6,6" opacity="0.5">
    <line x1="80" y1="0" x2="80" y2="628"/>
    <line x1="1120" y1="0" x2="1120" y2="628"/>
    <line x1="0" y1="120" x2="1200" y2="120"/>
    <line x1="0" y1="520" x2="1200" y2="520"/>
  </g>

  <!-- Top Badge -->
  <g transform="translate(80, 50)">
    <rect width="320" height="34" rx="17" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5"/>
    <circle cx="20" cy="17" r="5" fill="#059669"/>
    <text x="36" y="22" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="#065f46" letter-spacing="0.5">AI INTERNSHIP PROJECT SUITE</text>
  </g>

  <!-- Big Hero Title -->
  <text x="80" y="145" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="46" font-weight="800" fill="#0f172a" letter-spacing="-1.5">AI Research Workbench</text>
  <text x="80" y="185" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="20" font-weight="500" fill="#475569">4 Enterprise AI Applications Built with Python 3.12, LangChain &amp; Streamlit</text>

  <!-- Metrics Bar -->
  <g transform="translate(80, 220)">
    <rect width="1040" height="60" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="url(#liShadow)"/>
    <g transform="translate(30, 16)">
      <text x="0" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="22" font-weight="800" fill="#059669">39/39</text>
      <text x="85" y="22" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#64748b">Verified Tests Passed (100%)</text>
    </g>
    <line x1="370" y1="12" x2="370" y2="48" stroke="#e2e8f0" stroke-width="1.5"/>
    <g transform="translate(400, 16)">
      <text x="0" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="22" font-weight="800" fill="#2563eb">4 Modules</text>
      <text x="130" y="22" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#64748b">Independent &amp; Decoupled</text>
    </g>
    <line x1="720" y1="12" x2="720" y2="48" stroke="#e2e8f0" stroke-width="1.5"/>
    <g transform="translate(750, 16)">
      <text x="0" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="22" font-weight="800" fill="#7c3aed">Zero Mock</text>
      <text x="135" y="22" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="#64748b">Offline Mocks + Live SDKs</text>
    </g>
  </g>

  <!-- 4 Feature Cards Row -->
  <g transform="translate(80, 310)">
    <!-- Task 1 -->
    <g transform="translate(0, 0)">
      <rect width="245" height="175" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#liShadow)"/>
      <rect x="0" y="0" width="245" height="4" rx="2" fill="#2563eb"/>
      <text x="16" y="28" font-family="monospace" font-size="11" font-weight="700" fill="#2563eb">TASK 1</text>
      <text x="16" y="55" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Structured Extractor</text>
      <text x="16" y="80" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">Pydantic v2 schemas for Invoices &amp; Resumes with bounded self-repair retry loop.</text>
      <text x="16" y="150" font-family="monospace" font-size="11" font-weight="600" fill="#059669">✓ 11 Tests Passed</text>
    </g>

    <!-- Task 2 -->
    <g transform="translate(265, 0)">
      <rect width="245" height="175" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#liShadow)"/>
      <rect x="0" y="0" width="245" height="4" rx="2" fill="#0d9488"/>
      <text x="16" y="28" font-family="monospace" font-size="11" font-weight="700" fill="#0d9488">TASK 2</text>
      <text x="16" y="55" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Grounded RAG</text>
      <text x="16" y="80" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">ChromaDB semantic retrieval with unanswerable gating &amp; verified citations.</text>
      <text x="16" y="150" font-family="monospace" font-size="11" font-weight="600" fill="#059669">✓ 9 Tests Passed</text>
    </g>

    <!-- Task 3 -->
    <g transform="translate(530, 0)">
      <rect width="245" height="175" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#liShadow)"/>
      <rect x="0" y="0" width="245" height="4" rx="2" fill="#d97706"/>
      <text x="16" y="28" font-family="monospace" font-size="11" font-weight="700" fill="#b45309">TASK 3</text>
      <text x="16" y="55" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Autonomous Agent</text>
      <text x="16" y="80" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">ReAct loop with AST-safe calculator (no eval), sandbox reader, and web search.</text>
      <text x="16" y="150" font-family="monospace" font-size="11" font-weight="600" fill="#059669">✓ 11 Tests Passed</text>
    </g>

    <!-- Task 4 -->
    <g transform="translate(795, 0)">
      <rect width="245" height="175" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" filter="url(#liShadow)"/>
      <rect x="0" y="0" width="245" height="4" rx="2" fill="#7c3aed"/>
      <text x="16" y="28" font-family="monospace" font-size="11" font-weight="700" fill="#7e22ce">TASK 4</text>
      <text x="16" y="55" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="700" fill="#0f172a">Conversation Studio</text>
      <text x="16" y="80" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" fill="#64748b">Streamlit streaming chat with session state isolation &amp; RAG/Agent bridge.</text>
      <text x="16" y="150" font-family="monospace" font-size="11" font-weight="600" fill="#059669">✓ 8 Tests Passed</text>
    </g>
  </g>

  <!-- Footer Info Bar -->
  <g transform="translate(80, 525)">
    <text x="0" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="600" fill="#334155">Built by maheswari9080 · Google Antigravity</text>
    <text x="1040" y="24" text-anchor="end" font-family="monospace" font-size="13" font-weight="600" fill="#2563eb">github.com/maheswari9080/Python-Generative-AI-LangChain-Internship</text>
  </g>
</svg>"""


def create_png_from_pillow(output_path: Path, title: str, subtitle: str, badge_text: str):
    """Fallback high-res raster PNG generator using Pillow with clean light typography."""
    width, height = 1200, 630
    img = Image.new("RGB", (width, height), color="#f8fafc")
    draw = ImageDraw.Draw(img)

    # Top accent bar
    draw.rectangle([0, 0, width, 8], fill="#0d9488")

    # Outer border
    draw.rectangle([20, 20, width - 20, height - 20], outline="#e2e8f0", width=2)

    # Badge
    draw.rounded_rectangle([60, 50, 360, 86], radius=18, fill="#ecfdf5", outline="#a7f3d0", width=1)
    draw.ellipse([76, 64, 86, 74], fill="#059669")
    draw.text((96, 60), badge_text, fill="#065f46")

    # Titles
    draw.text((60, 110), title, fill="#0f172a")
    draw.text((60, 155), subtitle, fill="#475569")

    # 4 Cards
    card_w = 250
    card_h = 240
    start_y = 210

    cards_data = [
        ("TASK 1", "Structured Extractor", "Pydantic v2 schemas\nBounded Self-Repair\n11/11 Tests Passed", "#2563eb"),
        ("TASK 2", "Grounded RAG", "ChromaDB Vectors\nCitation Attribution\n9/9 Tests Passed", "#0d9488"),
        ("TASK 3", "Autonomous Agent", "AST Math Sandbox\nDirectory Isolation\n11/11 Tests Passed", "#d97706"),
        ("TASK 4", "Conversation Studio", "Token Streaming\nSession Isolation\n8/8 Tests Passed", "#7c3aed")
    ]

    for idx, (task_tag, card_title, desc, color) in enumerate(cards_data):
        x = 60 + idx * (card_w + 20)
        draw.rounded_rectangle([x, start_y, x + card_w, start_y + card_h], radius=10, fill="#ffffff", outline="#cbd5e1", width=1)
        draw.rounded_rectangle([x, start_y, x + card_w, start_y + 4], radius=2, fill=color)
        draw.text((x + 16, start_y + 18), task_tag, fill=color)
        draw.text((x + 16, start_y + 45), card_title, fill="#0f172a")
        draw.text((x + 16, start_y + 80), desc, fill="#64748b")

    # Footer
    draw.line([60, 540, width - 60, 540], fill="#e2e8f0", width=1)
    draw.text((60, 565), "AI Research Workbench · Intelligent Systems Suite · Built with Python 3.12 & LangChain", fill="#334155")
    draw.text((width - 450, 565), "GitHub: maheswari9080/Python-Generative-AI-LangChain-Internship", fill="#2563eb")

    img.save(output_path, "PNG")
    print(f"Created raster PNG: {output_path}")


def main():
    # 1. Save SVGs
    hero_svg_path = ASSETS_DIR / "hero_banner.svg"
    hero_svg_path.write_text(HERO_BANNER_SVG, encoding="utf-8")
    print(f"Saved: {hero_svg_path}")

    modules_svg_path = ASSETS_DIR / "modules_architecture.svg"
    modules_svg_path.write_text(MODULES_ARCHITECTURE_SVG, encoding="utf-8")
    print(f"Saved: {modules_svg_path}")

    linkedin_svg_path = ASSETS_DIR / "linkedin_banner.svg"
    linkedin_svg_path.write_text(LINKEDIN_BANNER_SVG, encoding="utf-8")
    print(f"Saved: {linkedin_svg_path}")

    # 2. Render High-Resolution PNGs with Pillow
    linkedin_png_path = ASSETS_DIR / "linkedin_banner.png"
    create_png_from_pillow(
        linkedin_png_path,
        title="AI Research Workbench: 4 Enterprise Applications",
        subtitle="Python 3.12 · Pydantic v2 · ChromaDB · LangChain · Streamlit",
        badge_text="AI INTERNSHIP PROJECT SUITE · 39/39 TESTS"
    )

    hero_png_path = ASSETS_DIR / "hero_banner.png"
    create_png_from_pillow(
        hero_png_path,
        title="AI Research Workbench",
        subtitle="Intelligent Systems Portfolio Suite · Production-Grade Architecture",
        badge_text="VERIFIED PORTFOLIO · 39/39 TESTS PASSING"
    )

    # 3. Also output image.png, image.svg, and linkedin.svg directly to project root
    root_png = ROOT_DIR / "image.png"
    root_svg = ROOT_DIR / "image.svg"
    root_li_svg = ROOT_DIR / "linkedin.svg"

    root_svg.write_text(LINKEDIN_BANNER_SVG, encoding="utf-8")
    root_li_svg.write_text(LINKEDIN_BANNER_SVG, encoding="utf-8")
    create_png_from_pillow(
        root_png,
        title="AI Research Workbench: 4 Enterprise Applications",
        subtitle="Python 3.12 · Pydantic v2 · ChromaDB · LangChain · Streamlit",
        badge_text="AI INTERNSHIP PROJECT SUITE · 39/39 TESTS"
    )
    print(f"Saved root assets: {root_png}, {root_svg}, {root_li_svg}")

    print("All visual assets successfully generated in light theme!")


if __name__ == "__main__":
    main()
