"""Gera assets/stats.svg e assets/languages.svg a partir da API do GitHub (sem servicos de terceiros)."""
import json, os, urllib.request
from collections import Counter
from html import escape

USER = os.environ.get("GH_USER", "ViktorGabriel")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
COLORS = {"TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Python": "#3776AB", "Java": "#ED8B00",
          "CSS": "#563D7C", "HTML": "#E34C26", "PowerShell": "#012456", "Shell": "#89E051", "Dockerfile": "#384D54"}
BG, BORDER, TITLE, TEXT, MUTED = "#0d1117", "#30363d", "#7AA2F7", "#c9d1d9", "#8b949e"


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    os.makedirs(OUT, exist_ok=True)
    user = api(f"/users/{USER}")
    repos, page = [], 1
    while True:
        chunk = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    repos = [r for r in repos if not r["fork"]]
    langs = Counter()
    for r in repos:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[k] += v
    stars = sum(r["stargazers_count"] for r in repos)
    forks = sum(r["forks_count"] for r in repos)
    rows = [("Repositorios publicos", len(repos)), ("Estrelas recebidas", stars), ("Forks", forks), ("Seguidores", user["followers"])]

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="190" viewBox="0 0 400 190" role="img" aria-label="Estatisticas do GitHub">',
         f'<rect x="0.5" y="0.5" width="399" height="189" rx="8" fill="{BG}" stroke="{BORDER}"/>',
         f'<text x="24" y="38" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="600" fill="{TITLE}">Estatisticas do GitHub</text>']
    for i, (k, v) in enumerate(rows):
        y = 78 + i * 30
        s.append(f'<text x="24" y="{y}" font-family="Segoe UI,Arial,sans-serif" font-size="14" fill="{MUTED}">{escape(k)}</text>')
        s.append(f'<text x="376" y="{y}" text-anchor="end" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="600" fill="{TEXT}">{v}</text>')
    s.append("</svg>")
    open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8").write("\n".join(s))

    top = langs.most_common(6)
    total = sum(v for _, v in top) or 1
    l = [f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="190" viewBox="0 0 400 190" role="img" aria-label="Linguagens mais usadas">',
         f'<rect x="0.5" y="0.5" width="399" height="189" rx="8" fill="{BG}" stroke="{BORDER}"/>',
         f'<text x="24" y="38" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="600" fill="{TITLE}">Linguagens mais usadas</text>']
    x = 24.0
    for name, v in top:
        w = 352 * v / total
        l.append(f'<rect x="{x:.1f}" y="54" width="{w:.1f}" height="8" fill="{COLORS.get(name, "#8b949e")}"/>')
        x += w
    for i, (name, v) in enumerate(top):
        cx, cy = 24 + (i % 2) * 180, 92 + (i // 2) * 28
        l.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{COLORS.get(name, "#8b949e")}"/>')
        l.append(f'<text x="{cx + 16}" y="{cy}" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="{TEXT}">{escape(name)} <tspan fill="{MUTED}">{100 * v / total:.1f}%</tspan></text>')
    l.append("</svg>")
    open(os.path.join(OUT, "languages.svg"), "w", encoding="utf-8").write("\n".join(l))


if __name__ == "__main__":
    main()
