# Painel de Projetos — PME (atualização automática)

Painel de TV do portfólio de projetos, publicado no GitHub Pages e **atualizado
automaticamente** a partir da base Notion "Projetos PME".

## Como funciona
- `panel_template.html` — o layout do painel (não muda no dia a dia).
- `generate.py` — lê a base do Notion e gera o `index.html`.
- `.github/workflows/update-panel.yml` — roda de segunda a sexta, às **07h e 13h**
  (horário de Brasília), regenera o `index.html` e publica sozinho.
- `index.html` — o arquivo que o GitHub Pages mostra na TV (gerado automaticamente).

## Configuração (uma única vez)
1. **Criar o token do Notion:** em https://www.notion.so/my-integrations →
   *New integration* → nome "GitHub Painel PME", workspace da PME, capacidade
   *Read content*. Copie o **Internal Integration Secret**.
2. **Dar acesso à base:** abra a base "Projetos PME" no Notion → menu `•••` (canto
   superior direito) → *Connections* → adicione a integração "GitHub Painel PME".
3. **Guardar o token no GitHub:** no repositório → *Settings* → *Secrets and
   variables* → *Actions* → *New repository secret* → nome **`NOTION_TOKEN`**,
   valor = o token copiado.
4. **Permitir que o robô publique:** *Settings* → *Actions* → *General* →
   *Workflow permissions* → marque **Read and write permissions** → *Save*.

## Rodar na hora (teste)
Aba **Actions** → "Atualizar Painel de Projetos" → **Run workflow**.
Em ~1 minuto o `index.html` é atualizado e o Pages reflete na TV.
