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
    rows = ""
    for i, (name, count, color_key) in enumerate(languages):
        y = 73 + i * 39
        bar_width = round(276 * count / n, 2)
        rows += (f'<text x="415" y="{y}" fill="{c["ink"]}" font-size="19" font-family="Arial,sans-serif">{escape(name)}</text>\n'
                 f'<rect x="548" y="{y-15}" width="276" height="16" rx="8" fill="{c["soft"]}" opacity=".35"/>\n'
                 f'<rect x="548" y="{y-15}" width="{bar_width}" height="16" rx="8" fill="{c[color_key]}"/>\n'
                 f'<text x="851" y="{y}" font-size="18" text-anchor="end" fill="{c["muted"]}" font-family="Arial,sans-serif">{count} <tspan font-size="13">repos</tspan></text>\n')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="245" viewBox="0 0 920 245" role="img" aria-label="Estatísticas dos repositórios públicos de Christian Oliveira">
<rect x="1" y="1" width="918" height="243" rx="15" fill="{c['bg']}" stroke="{c['stroke']}" stroke-width="2"/>
<path d="M383 27V216" stroke="{c['stroke']}" stroke-width="1"/>
<text x="32" y="39" fill="{c['muted']}" font-family="Arial,sans-serif" font-size="15" letter-spacing="2">GITHUB / VISÃO GERAL</text>
<text x="29" y="161" fill="{c['ink']}" font-family="Georgia,serif" font-weight="700" font-size="115">{n}</text>
<text x="33" y="194" fill="{c['ink']}" font-family="Arial,sans-serif" font-weight="700" font-size="20">repositórios públicos</text>
<text x="33" y="221" fill="{c['muted']}" font-family="Arial,sans-serif" font-size="14">Dados públicos da conta</text>
<text x="415" y="39" fill="{c['muted']}" font-family="Arial,sans-serif" font-size="15" letter-spacing="1">LINGUAGEM PRINCIPAL POR REPOSITÓRIO</text>
{rows}</svg>'''

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
