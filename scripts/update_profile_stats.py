#!/usr/bin/env python3
"""Atualiza SVGs locais do perfil usando apenas dados públicos do GitHub.

Sem dependências de terceiros. As métricas representam repositórios públicos
e a linguagem principal que o próprio GitHub atribui a cada repositório.
Não representam commits privados, tempo de uso, nem porcentagem de código.
"""
from collections import Counter
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

USERNAME = "Christian5910"
ROOT = Path(__file__).resolve().parents[1]
PALETTES = {
  'light': {
    'bg': "#F5F0E4",
    'stroke': "#D4C8AE",
    'ink': "#1D2E4A",
    'muted': "#4A5567",
    'soft': "#C7BB98",
    'bar': "#315E8E",
    'bar2': "#7091AC",
    'bar3': "#B8A178",
    'bar4': "#A6A4A0"
  },
  'dark': {
    'bg': "#18263A",
    'stroke': "#43536C",
    'ink': "#F1ECDC",
    'muted': "#BEC9D5",
    'soft': "#63728B",
    'bar': "#91B8EA",
    'bar2': "#6B96BB",
    'bar3': "#C1A476",
    'bar4': "#9098A4"
  }
}
LANGS = [("JavaScript", "bar"), ("HTML", "bar2"), ("Python", "bar3")]

def fetch_repos():
    token = os.getenv("GITHUB_TOKEN")
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&page={page}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "Christian5910-profile-readme"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        with urlopen(Request(url, headers=headers), timeout=20) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("Resposta inesperada da API de repositórios")
        repos.extend(repo for repo in batch if not repo.get("private", False))
        if len(batch) < 100:
            break
        page += 1
    if not repos:
        raise RuntimeError("Nenhum repositório público retornado; gráficos antigos preservados")
    return repos

def render(theme, n, languages):
    c = PALETTES[theme]
    dark = theme == "dark"
    ink = "#F7F1E6" if dark else "#1D2E4A"
    soft = "#C0D0E0" if dark else "#5F6671"
    bg = "#18283E" if dark else "#F1ECDC"
    border = "#516784" if dark else "#C7BB98"
    track = "#354A66" if dark else "#D4D8D4"
    shades = {
        "bar": "#8DBCEB" if dark else "#2C4268",
        "bar2": "#75A8CE" if dark else "#507EA6",
        "bar3": "#CEAD70" if dark else "#AA844B",
        "bar4": "#A6B2C5" if dark else "#79818D",
    }
    rows = []
    labels = []
    for i, (name, count, color_key) in enumerate(languages):
        y = 104 + i * 49
        width = max(0, min(210, 210 * count / n))
        rows.append(
            f'<text x="405" y="{y}" font-size="21" fill="{ink}" font-family="Arial,sans-serif">{escape(name)}</text>'
            f'<rect x="555" y="{y-17}" width="214" height="19" rx="9.5" fill="{track}"/>'
            f'<rect x="555" y="{y-17}" width="{width:.2f}" height="19" rx="9.5" fill="{shades[color_key]}"/>'
            f'<text x="798" y="{y}" font-family="Arial,sans-serif" font-weight="700" font-size="23" fill="{ink}">{count}</text>'
            f'<text x="824" y="{y}" font-family="Arial,sans-serif" font-size="14" fill="{soft}">repos</text>'
        )
        labels.append(f"{name}: {count}")
    desc = escape(f"{n} repositórios públicos. " + ", ".join(labels))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="305" viewBox="0 0 960 305" role="img" aria-labelledby="title desc">
<title id="title">Estatísticas públicas do GitHub de Christian5910</title><desc id="desc">{desc}</desc>
<rect x="2" y="2" width="956" height="301" rx="17" fill="{bg}" stroke="{border}" stroke-width="2"/>
<path d="M376 24V281" stroke="{border}" stroke-width="1.5"/>
<text x="34" y="43" font-family="Arial,sans-serif" font-size="17" letter-spacing="1.3" font-weight="700" fill="{soft}">GITHUB / VISÃO GERAL</text>
<text x="35" y="181" font-family="Georgia,serif" font-size="100" font-weight="700" fill="{ink}">{n}</text>
<text x="36" y="220" font-family="Arial,sans-serif" font-size="24" font-weight="700" fill="{ink}">repositórios públicos</text>
<text x="36" y="260" font-family="Arial,sans-serif" font-size="16" fill="{soft}">Código, design e experimentação</text>
<text x="403" y="43" font-family="Arial,sans-serif" font-size="16" letter-spacing=".5" font-weight="700" fill="{soft}">LINGUAGEM PRINCIPAL</text>
{''.join(rows)}
</svg>'''


def main():
    repos = fetch_repos()
    n = len(repos)
    language_counts = Counter(repo.get("language") or "Outra" for repo in repos)
    languages = [(name, language_counts.pop(name, 0), color) for name, color in LANGS]
    languages.append(("Outras", sum(language_counts.values()), "bar4"))
    for theme in PALETTES:
        output = ROOT / "assets" / f"stats-{theme}.svg"
        output.parent.mkdir(parents=True, exist_ok=True)
        content = render(theme, n, languages)
        if not output.exists() or output.read_text(encoding="utf-8") != content:
            output.write_text(content, encoding="utf-8")
    print(f"Atualizados dados de {n} repositórios públicos.")

if __name__ == "__main__":
    main()
