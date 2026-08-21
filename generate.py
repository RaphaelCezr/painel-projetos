#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o index.html do Painel de Projetos a partir da base Notion "Projetos PME".
Uso: NOTION_TOKEN=secret_xxx python generate.py

- Lê o template panel_template.html (com os marcadores __SNAPSHOT__ e __RAW__).
- Consulta a base no Notion, monta a lista de projetos e escreve index.html.
- Não altera mais nada do template (layout/estilo/JS ficam intactos).
"""
import os, sys, json, datetime, urllib.request, urllib.error

# ---- Configuração (pode sobrescrever por variáveis de ambiente) ----
DATA_SOURCE_ID = os.environ.get("NOTION_DATA_SOURCE_ID", "9a0f40f4-a897-4084-abd8-8ff8b70c8735")
DATABASE_ID    = os.environ.get("NOTION_DATABASE_ID",    "a98078e362594348bba304f693e00706")
TOKEN          = os.environ.get("NOTION_TOKEN", "").strip()
TEMPLATE       = os.environ.get("TEMPLATE_FILE", "panel_template.html")
OUTPUT         = os.environ.get("OUTPUT_FILE", "index.html")

if not TOKEN:
    sys.exit("ERRO: variável de ambiente NOTION_TOKEN não definida.")

# ---- Chamada HTTP simples ao Notion ----
def _post(url, version):
    results, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Notion-Version": version,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results.extend(data.get("results", []))
        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break
    return results

def fetch_pages():
    """Tenta a API nova (data sources) e cai para a clássica (databases)."""
    attempts = [
        (f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query", "2025-09-03"),
        (f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", "2022-06-28"),
        (f"https://api.notion.com/v1/databases/{DATA_SOURCE_ID}/query", "2022-06-28"),
    ]
    last_err = None
    for url, version in attempts:
        try:
            pages = _post(url, version)
            print(f"OK via {url} (Notion-Version {version}) — {len(pages)} páginas")
            return pages
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:300]
            print(f"Falhou {url} ({version}): HTTP {e.code} {detail}")
            last_err = e
        except Exception as e:
            print(f"Falhou {url} ({version}): {e}")
            last_err = e
    raise SystemExit(f"ERRO: não foi possível consultar o Notion. Último erro: {last_err}")

# ---- Extração dos valores por tipo de propriedade ----
def prop_text(p):
    if not p: return ""
    t = p.get("type")
    if t in ("title", "rich_text"):
        return "".join(x.get("plain_text", "") for x in p.get(t, [])).strip()
    if t == "select":
        return (p.get("select") or {}).get("name", "") or ""
    if t == "status":
        return (p.get("status") or {}).get("name", "") or ""
    if t == "people":
        return ", ".join(x.get("name", "") for x in p.get("people", [])).strip()
    return ""

def prop_multi(p):
    if not p: return []
    if p.get("type") == "multi_select":
        return [x.get("name", "") for x in p.get("multi_select", []) if x.get("name")]
    return []

def normalize(pages):
    records = []
    for pg in pages:
        pr = pg.get("properties", {})
        n = prop_text(pr.get("Nome do Projeto"))
        if not n:
            continue  # ignora fichas sem nome
        nx = prop_text(pr.get("Próximo passo"))
        if not nx or nx.upper() == "NA":
            nx = "—"
        records.append({
            "n": n,
            "s": prop_text(pr.get("Status")) or "Em andamento",
            "a": prop_multi(pr.get("Área")),
            "ano": prop_text(pr.get("Ano")),
            "r": prop_text(pr.get("Responsável")),
            "nx": nx,
        })
    records.sort(key=lambda x: x["n"].lower())
    return records

# ---- Render ----
def render(records):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    # Fuso de Brasília (America/Sao_Paulo = UTC-3, sem horário de verão desde 2019)
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
    snapshot = now.strftime("%d/%m/%Y às %H:%M")
    raw_js = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    out = tpl.replace("__SNAPSHOT__", snapshot).replace("__RAW__", raw_js)
    open(OUTPUT, "w", encoding="utf-8").write(out)
    print(f"index.html gerado: {len(records)} projetos · snapshot {snapshot}")

if __name__ == "__main__":
    render(normalize(fetch_pages()))
