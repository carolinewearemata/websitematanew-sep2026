# Novo site da MATA (português)

Primeira versão navegável do site, construída a partir de `conteudo/MATA_SITE_PACOTE_PARA_CLAUDE.md` (copy) e do caderno editorial, com o Brand OS 2.4 e os logos oficiais.

## Como gerar

```bash
pip install fonttools brotli   # só se for refazer o subset das fontes
python3 site/build.py
```

O script gera duas saídas a partir das mesmas páginas:

| Pasta | Para que serve |
| --- | --- |
| `dist/` | Site estático com uma página HTML por URL (`/pt`, `/pt/como-funciona`...), CSS, JS, fontes, `sitemap.xml` e `robots.txt`. É a base para publicar. |
| `preview/index.html` | Prévia em arquivo único para aprovação. Cada página vira uma vista com o próprio H1, navegável por `#rota`. |

## Estrutura

- `site/build.py`: páginas, metadados de busca, JSON-LD e conversão dos quatro artigos do pacote (texto integral, sem edição).
- `site/src/site.css` e `site/src/site.js`: sistema visual e interações (menu, cena do antes e depois, RPM, preferência de assinatura, formulário).
- `site/assets/`: Stack Sans (subset woff2 das fontes do pacote), logos oficiais preto e branco, gradiente oficial em webp.

## Rotas

`/pt`, `/pt/como-funciona`, `/pt/mecanismos`, `/pt/assinatura`, `/pt/reposicionamento-de-marca`, `/pt/resultados`, `/pt/sobre` (âncora `#principios`), `/pt/blog`, `/pt/contato` e os quatro artigos em `/pt/blog/...`. A migração das rotas atuais (`/pt/how-it-works` etc.) ainda precisa dos redirecionamentos definidos no pacote.

## Antes de publicar

- Formulário: definir `window.MATA_FORM_ENDPOINT` (POST JSON). Sem endpoint, o envio mostra a mensagem de falha com o e-mail da MATA.
- Artigos: preencher a data efetiva de publicação (visível e em `datePublished`) no momento da publicação.
- Conferir títulos, canonical, sitemap e indexação no ambiente publicado.
- Fontes: o pacote traz a licença Befonts (uso comercial); confirmar o uso web antes de publicar.
