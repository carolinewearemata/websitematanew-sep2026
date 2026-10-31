#!/usr/bin/env python3
"""Gera o site da MATA em português.

Saídas:
  dist/      site estático com as rotas /pt/... (uma página HTML por URL)
  preview/   prévia navegável em arquivo único, com uma vista por página (#rota)

Uso: python3 site/build.py
"""
import base64
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "src"
ASSETS = ROOT / "site" / "assets"
PACOTE = ROOT / "conteudo" / "MATA_SITE_PACOTE_PARA_CLAUDE.md"
DOMAIN = "https://wearemata.co"
EMAIL = "hello@wearemata.company"
LINKEDIN_MATA = "https://www.linkedin.com/company/wearemata/"
LINKEDIN_CAROL = "https://www.linkedin.com/in/mirandamcaroline/"

# chave: (rota publicada, título para busca, descrição para busca, seção do menu)
ROUTES = {
    "inicio": ("/pt", "MATA, seu time de marketing por assinatura",
               "Conheça o modelo de marketing da MATA, um time de pessoas e inteligência artificial que trabalha por dentro da empresa e cuida da rotina de marketing.", "inicio"),
    "como-funciona": ("/pt/como-funciona", "Como funciona o time de marketing da MATA",
                      "Entenda como o time se integra à empresa, quais decisões ficam com a liderança e onde a inteligência artificial entra no trabalho.", "como-funciona"),
    "mecanismos": ("/pt/mecanismos", "Shadowing, RPM e a rotina de marketing da MATA",
                   "Acompanhe uma dúvida de vendas até a próxima entrega e conheça o ranking de prioridades, a memória da marca e os rituais da MATA.", "como-funciona"),
    "assinatura": ("/pt/assinatura", "Marketing por assinatura mensal ou anual com a MATA",
                   "Compare as modalidades e entenda como combinar dedicação do time, produção do AI Lab e projetos especializados. Converse com a MATA para saber o valor.", "assinatura"),
    "reposicionamento-de-marca": ("/pt/reposicionamento-de-marca", "Reposicionamento de marca com a MATA",
                                  "Veja como a MATA investiga o que mudou no negócio, define a direção da marca e acompanha sua aplicação em vendas, site e materiais.", "como-funciona"),
    "resultados": ("/pt/resultados", "Resultados da MATA em cinco negócios",
                   "Conheça cinco trabalhos de marketing integrado, do relançamento de um portfólio de saúde à criação de uma marca de consumo.", "resultados"),
    "sobre": ("/pt/sobre", "Sobre a MATA e sua fundadora Caroline Miranda Martha",
              "Conheça a origem da MATA, sua relação com a tecnologia e os princípios que orientam o trabalho do time dentro das empresas.", "como-funciona"),
    "blog": ("/pt/blog", "Blog da MATA sobre estrutura de marketing, marca e IA",
             "Guias do time MATA e artigos de Caroline Miranda Martha sobre como estruturar marketing, aplicar um reposicionamento e trabalhar com inteligência artificial.", "blog"),
    "contato": ("/pt/contato", "Fale com a MATA sobre a sua empresa",
                "Conte quem cuida do marketing hoje e o que você precisa resolver. Converse com o time da MATA sobre dedicação, assinatura e proposta.", "contato"),
    "blog-como-estruturar-a-area-de-marketing": ("/pt/blog/como-estruturar-a-area-de-marketing", "Como estruturar a área de marketing quando a empresa já cresceu",
                                                 "Compare estruturas de equipe, distribua responsabilidades e organize os primeiros 90 dias de marketing em uma empresa que já vende.", "blog"),
    "blog-produzir-marketing-nao-e-conduzir-marketing": ("/pt/blog/produzir-marketing-nao-e-conduzir-marketing", "Produzir marketing não é conduzir marketing",
                                                         "Caroline Miranda Martha discute o que a IA muda na produção e por que tantas decisões de marketing continuam voltando para a liderança.", "blog"),
    "blog-como-implementar-o-reposicionamento-de-marca": ("/pt/blog/como-implementar-o-reposicionamento-de-marca", "Como implementar o reposicionamento de marca na prática",
                                                          "Um teste com a próxima proposta comercial ajuda a descobrir onde a marca aprovada já funciona e onde a empresa ainda conta a história antiga.", "blog"),
    "blog-pensar-no-sistema": ("/pt/blog/pensar-no-sistema", "Quando vale criar um sistema de marketing com IA",
                               "Uma conversa sobre materiais de produto mostra quando compensa registrar critérios, reaproveitar decisões e rever o trabalho com ajuda da IA.", "blog"),
    "404": ("/pt/404", "Página não encontrada | MATA", "Não encontramos essa página.", ""),
}

ARTICLES = {
    "Artigo do blog 01": ("blog-como-estruturar-a-area-de-marketing", "time"),
    "Artigo do blog 02": ("blog-produzir-marketing-nao-e-conduzir-marketing", "caroline"),
    "Artigo do blog 03": ("blog-como-implementar-o-reposicionamento-de-marca", "caroline"),
    "Artigo do blog 04": ("blog-pensar-no-sistema", "caroline"),
}


class Linker:
    def __init__(self, mode):
        self.mode = mode

    def __call__(self, key):
        anchor = ""
        if key == "principios":
            if self.mode == "preview":
                return "#principios"
            key, anchor = "sobre", "#principios"
        if self.mode == "preview":
            return "#" + key
        return ROUTES[key][0] + anchor

    def from_path(self, path):
        """Converte uma rota do pacote (/pt/...) em link desta saída."""
        path = path.strip()
        if path == "/pt/sobre#principios":
            return self("principios")
        if path in ("/pt", "/pt/"):
            return self("inicio")
        if path.startswith("/pt/blog/"):
            return self("blog-" + path[len("/pt/blog/"):])
        if path.startswith("/pt/"):
            return self(path[len("/pt/"):])
        return path


def esc(text):
    return html.escape(text, quote=True)


# ---------------------------------------------------------------- marca
def logo_svg(label="MATA"):
    raw = (ASSETS / "logos" / "mata-logo-preto.svg").read_text()
    paths = re.findall(r'<path d="([^"]+)"', raw)
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    inner = "".join(f'<path d="{d}"/>' for d in paths)
    return f'<svg viewBox="{vb}" role="img" aria-label="{label}"><title>{label}</title>{inner}</svg>'


BLOB = ("data:image/svg+xml;utf8," +
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><path d='M152 38c22 18 36 48 30 78-6 31-32 57-63 66-31 9-66 1-88-21C9 139 3 104 14 76 25 47 54 24 86 19c24-4 48 3 66 19z'/></svg>")


# ---------------------------------------------------------------- moldura
def header(L, current_section):
    def cur(key):
        return ' aria-current="page"' if current_section == key else ""
    sub_current = " is-current" if current_section == "como-funciona" else ""
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo.</a>
<header class="site-head">
  <div class="wrap">
    <a class="logo" href="{L('inicio')}" data-nav="inicio">{logo_svg('MATA, voltar ao início')}</a>
    <nav class="nav" aria-label="Principal">
      <a href="{L('inicio')}" data-nav="inicio"{cur('inicio')}>Início</a>
      <div class="sub">
        <button type="button" class="sub-btn{sub_current}" id="sub-btn" aria-expanded="false" aria-controls="sub-panel">Como funciona <svg class="chev" viewBox="0 0 10 10" aria-hidden="true"><path d="M1 3l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>
        <div class="sub-panel" id="sub-panel" hidden>
          <a href="{L('como-funciona')}" data-nav="como-funciona"><b>Como funciona</b></a>
          <a href="{L('mecanismos')}" data-nav="mecanismos"><b>Mecanismos e rituais</b></a>
          <a href="{L('reposicionamento-de-marca')}" data-nav="reposicionamento-de-marca"><b>Reposicionamento de marca</b></a>
          <a href="{L('sobre')}" data-nav="sobre"><b>Sobre a MATA</b></a>
        </div>
      </div>
      <a href="{L('assinatura')}" data-nav="assinatura"{cur('assinatura')}>Assinatura</a>
      <a href="{L('resultados')}" data-nav="resultados"{cur('resultados')}>Resultados</a>
      <a href="{L('blog')}" data-nav="blog"{cur('blog')}>Blog</a>
      <a class="btn" href="{L('contato')}" data-nav="contato"{cur('contato')}>Falar com a MATA</a>
    </nav>
    <button type="button" class="menu-btn" id="menu-btn" aria-expanded="false" aria-controls="mobile-nav"><i aria-hidden="true"></i>Menu</button>
  </div>
  <div class="mobile-nav" id="mobile-nav" hidden>
    <nav class="wrap" aria-label="Principal no celular">
      <a href="{L('inicio')}" data-nav="inicio"{cur('inicio')}>Início</a>
      <a href="{L('como-funciona')}" data-nav="como-funciona">Como funciona</a>
      <a class="sub-item" href="{L('mecanismos')}" data-nav="mecanismos">Mecanismos e rituais</a>
      <a class="sub-item" href="{L('reposicionamento-de-marca')}" data-nav="reposicionamento-de-marca">Reposicionamento de marca</a>
      <a class="sub-item" href="{L('sobre')}" data-nav="sobre">Sobre a MATA</a>
      <a href="{L('assinatura')}" data-nav="assinatura"{cur('assinatura')}>Assinatura</a>
      <a href="{L('resultados')}" data-nav="resultados"{cur('resultados')}>Resultados</a>
      <a href="{L('blog')}" data-nav="blog"{cur('blog')}>Blog</a>
      <a class="btn" href="{L('contato')}" data-nav="contato">Falar com a MATA</a>
    </nav>
  </div>
</header>'''


def footer(L):
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div>
      <a class="logo" href="{L('inicio')}">{logo_svg('MATA')}</a>
      <p>MATA, um time de marketing por assinatura que reúne pessoas e tecnologia dentro da sua empresa.</p>
    </div>
    <nav aria-label="Todas as páginas">
      <a href="{L('inicio')}">Início</a>
      <a href="{L('como-funciona')}">Como funciona</a>
      <a href="{L('assinatura')}">Assinatura</a>
      <a href="{L('mecanismos')}">Mecanismos e rituais</a>
      <a href="{L('reposicionamento-de-marca')}">Reposicionamento de marca</a>
      <a href="{L('resultados')}">Resultados</a>
      <a href="{L('sobre')}">Sobre a MATA</a>
      <a href="{L('blog')}">Blog</a>
      <a href="{L('contato')}">Falar com a MATA</a>
    </nav>
    <div class="contact">
      <a href="{LINKEDIN_MATA}" target="_blank" rel="noopener">LinkedIn da MATA</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
  </div>
</footer>'''


def more(href, text):
    ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return f'<a class="more" href="{href}"{ext}>{text} <span aria-hidden="true">→</span></a>'


# ---------------------------------------------------------------- páginas
def page_inicio(L):
    return f'''
<section class="gradient hero" aria-labelledby="h-inicio">
  <div class="wrap">
    <div>
      <h1 id="h-inicio">Um modelo de marketing para a nossa nova realidade</h1>
      <p class="lead">Com a MATA, sua empresa passa a ter um time de marketing por assinatura. Trabalhamos junto de quem vende e de quem conhece o produto, usamos inteligência artificial para reunir o que a empresa sabe e cuidamos do que vem depois, desde escolher a prioridade até colocar o trabalho na rua.</p>
      <div class="actions">
        <a class="btn" href="{L('assinatura')}">Como funciona a assinatura <span class="arr" aria-hidden="true">→</span></a>
        <a class="btn line" href="{L('contato')}">Falar com a MATA</a>
      </div>
    </div>
    <div class="couple" role="group" aria-label="Quem faz o quê">
      <div class="mod empresa"><span class="who">Sua empresa</span><p>Conhece o negócio e decide o que é da liderança.</p></div>
      <div class="bridge" aria-hidden="true"></div>
      <div class="mod time"><span class="who">Time MATA</span><p>Ouve quem vende, ajuda a decidir o que fazer e faz o trabalho andar.</p></div>
      <div class="bridge" aria-hidden="true"></div>
      <div class="mod ia"><span class="who">Inteligência artificial</span><p>Ajuda o time a lembrar o que aprendeu sobre a empresa.</p></div>
    </div>
  </div>
</section>

<section class="band surface" aria-labelledby="h-quem-cuida">
  <div class="wrap">
    <div class="head">
      <h2 id="h-quem-cuida">Quem cuida do marketing quando você está em outra reunião?</h2>
      <p class="lead">Às vezes, a empresa cresceu sem montar um time de marketing. Outras vezes, já tem gente fazendo um bom trabalho, só que em lugares diferentes. O sinal costuma ser parecido, basta o comercial precisar de uma apresentação nova para tudo passar pela mesma pessoa outra vez.</p>
    </div>
    <table class="compare">
      <thead><tr><th scope="col">Na rotina da empresa</th><th scope="col">Antes da MATA</th><th scope="col" class="with">Com a MATA</th></tr></thead>
      <tbody>
        <tr><th scope="row">Vendas precisa de uma apresentação</th>
          <td class="before" data-label="Antes da MATA"><p>A direção procura os arquivos, explica o produto e junta os comentários.</p><span class="desk">Volta para a mesma pessoa</span></td>
          <td class="with" data-label="Com a MATA"><p>Nosso time ouve quem vai usar a apresentação, confere as informações com produto e leva uma versão para vendas testar.</p></td></tr>
        <tr><th scope="row">Dois pedidos chegam com urgência</th>
          <td class="before" data-label="Antes da MATA"><p>Cada pessoa vê o próprio prazo, alguém da liderança precisa escolher qual atrasa.</p><span class="desk">Volta para a mesma pessoa</span></td>
          <td class="with" data-label="Com a MATA"><p>Mostramos o que cada escolha muda na semana, recomendamos uma ordem e ajustamos o trabalho com você.</p></td></tr>
        <tr><th scope="row">Um cliente aponta uma informação errada</th>
          <td class="before" data-label="Antes da MATA"><p>Quem recebeu o aviso corrige a própria cópia. Outra versão continua circulando.</p></td>
          <td class="with" data-label="Com a MATA"><p>Conferimos a informação com quem responde por ela, atualizamos a referência da marca e identificamos os materiais que precisam da correção.</p></td></tr>
      </tbody>
    </table>
  </div>
</section>

<section class="band" aria-labelledby="h-cena">
  <div class="wrap">
    <div class="scene-head">
      <div>
        <span class="demo-tag">Exemplo ilustrativo, com informações fictícias</span>
        <h2 id="h-cena">“Dá para trocar de sistema sem parar a operação?”</h2>
      </div>
      <p class="lead">Imagine que você venda um sistema e ouça essa pergunta numa reunião. Hoje já dá para pedir à IA uma apresentação sobre o assunto e ter os slides na mesma tarde. O que eles deveriam dizer, se a resposta depende de como cada cliente trabalha?</p>
    </div>

    <div class="board">
      <div class="colhead before" aria-hidden="true">Antes da MATA</div>
      <div class="colhead mid" aria-hidden="true"></div>
      <div class="colhead with" aria-hidden="true">Com a MATA</div>
      <div class="spine" aria-hidden="true"><i></i></div>

      <div class="moment">
        <div class="question gradient"><p class="label">Entrada</p><p style="margin:0;font:400 clamp(1.15rem,1.8vw,1.4rem)/1.35 var(--font-display);color:var(--on-gradient)">Um comprador faz a pergunta numa reunião de vendas.</p></div>
      </div>

      <section class="moment" aria-labelledby="m1">
        <h3 class="m-label" id="m1"><span><b>1</b>Quem ouviu</span></h3>
        <div class="cell before" data-label="Antes da MATA">
          <p>Só quem estava vendendo. Vendas vai perguntar à implantação.</p>
          <div class="who-row"><span class="who-chip"><b>Ouviu</b> vendas</span></div>
        </div>
        <div class="node" aria-hidden="true"></div>
        <div class="cell with" data-label="Com a MATA">
          <p>O time MATA ouve a pergunta na reunião e registra o que precisa confirmar com implantação.</p>
          <div class="artifact">
            <div class="a-top"><span>Registro de shadowing</span><span>Fictício</span></div>
            <dl>
              <div><dt>Pergunta do comprador</dt><dd>“Dá para trocar de sistema sem parar a operação?”</dd></div>
              <div><dt>Exemplo que o vendedor usou</dt><dd>Um cliente que migrou por etapas.</dd></div>
              <div><dt>Confirmar com implantação</dt><dd><span class="hl">Em quais casos a troca pede uma pausa na operação.</span></dd></div>
            </dl>
          </div>
          <div class="who-row"><span class="who-chip"><b>Percebeu</b> time MATA, no shadowing</span></div>
        </div>
      </section>

      <section class="moment" aria-labelledby="m2">
        <h3 class="m-label" id="m2"><span><b>2</b>De onde vem a resposta</span></h3>
        <div class="cell before" data-label="Antes da MATA">
          <p>Implantação explica ao vendedor por mensagem. A apresentação de amanhã está com outra pessoa. Quem junta as duas conversas?</p>
          <div class="who-row"><span class="who-chip"><b>Juntou</b> você</span></div>
          <span class="desk">Na sua mesa: explicar o produto de novo</span>
        </div>
        <div class="node" aria-hidden="true"></div>
        <div class="cell with" data-label="Com a MATA">
          <p>A IA recupera a orientação existente, uma pessoa confere em quais situações ela se aplica.</p>
          <div class="mem">
            <div class="ai"><small>A IA encontrou na memória da marca</small>“A troca pode ser feita por etapas.”</div>
            <div class="glass" aria-hidden="true"></div>
            <div class="person"><small>Uma pessoa conferiu com implantação</small>Vale quando os dois sistemas podem funcionar juntos por um período. Muda quando a operação depende de uma integração que só existe no sistema antigo.</div>
          </div>
          <div class="who-row"><span class="who-chip"><b>Encontrou</b> IA</span><span class="who-chip"><b>Conferiu</b> time MATA com implantação</span></div>
        </div>
      </section>

      <section class="moment" aria-labelledby="m3">
        <h3 class="m-label" id="m3"><span><b>3</b>O que vem primeiro</span></h3>
        <div class="cell before" data-label="Antes da MATA">
          <p>Cada pessoa vê o próprio prazo, alguém da liderança precisa escolher qual atrasa.</p>
          <div class="slips">
            <div class="slip"><b>Post previsto da semana</b><span>sexta</span><span>conteúdo</span></div>
            <div class="slip"><b>Apresentação para o comprador</b><span>amanhã</span><span>vendas</span></div>
            <div class="slip"><b>Página do produto</b><span>sem data</span><span>site</span></div>
          </div>
          <div class="who-row"><span class="who-chip"><b>Escolheu</b> você</span></div>
          <span class="desk">Na sua mesa: decidir qual atrasa</span>
        </div>
        <div class="node" aria-hidden="true"></div>
        <div class="cell with" data-label="Com a MATA">
          <p>A apresentação de amanhã passa para o primeiro lugar. O post pode esperar.</p>
          <div class="artifact rpm-card">
            <div class="a-top"><span>RPM, ranking de prioridades</span><output data-planned="Ordem planejada" data-final="Ordem depois do shadowing">Ordem depois do shadowing</output></div>
            <ol class="rpm-list">
              <li data-final="1" data-planned="3"><span class="pos">1</span><span><span class="t">Apresentação para o comprador</span><span class="r">Corrigir a explicação antes da reunião de amanhã.</span></span><span class="mv up">Era 3º</span></li>
              <li data-final="2" data-planned="2"><span class="pos">2</span><span><span class="t">Trecho do site sobre a troca</span><span class="r">Rever com a pessoa que cuida da implantação.</span></span><span class="mv">Era 2º</span></li>
              <li data-final="3" data-planned="1"><span class="pos">3</span><span><span class="t">Post previsto da semana</span><span class="r">Retomar depois dessas duas mudanças.</span></span><span class="mv">Era 1º</span></li>
            </ol>
            <button type="button" class="replay" hidden>Ver a ordem mudar de novo</button>
          </div>
          <div class="who-row"><span class="who-chip"><b>Recomendou</b> time MATA</span><span class="who-chip"><b>Aprovou</b> você</span></div>
          <span class="good">Sua palavra: aprovar a nova ordem</span>
        </div>
      </section>

      <section class="moment" aria-labelledby="m4">
        <h3 class="m-label" id="m4"><span><b>4</b>A apresentação de amanhã</span></h3>
        <div class="cell before" data-label="Antes da MATA">
          <p>Os slides ficam prontos na mesma tarde, com a explicação de sempre.</p>
          <div class="slide old" role="img" aria-label="Slide fictício: Migração simples e sem complicação. Nossa equipe cuida de tudo para você.">
            <span class="s-title">Migração simples e sem complicação</span>
            <span class="s-body">Nossa equipe cuida de tudo para você.</span>
            <span class="s-foot">Slide 7</span>
          </div>
          <div class="who-row"><span class="who-chip"><b>Usou</b> vendas</span></div>
        </div>
        <div class="node" aria-hidden="true"></div>
        <div class="cell with" data-label="Com a MATA">
          <p>Vendas usa a nova versão, com a resposta que implantação confirmou.</p>
          <div class="slide new" role="img" aria-label="Slide fictício revisado: Como a sua operação continua durante a troca. Na maioria dos casos, os dois sistemas funcionam juntos até a equipe estar pronta. Se a operação depende de uma integração do sistema antigo, a implantação avalia o seu caso antes da proposta.">
            <span class="s-title">Como a sua operação continua durante a troca</span>
            <span class="s-body"><span class="hl">Na maioria dos casos, os dois sistemas funcionam juntos até a equipe estar pronta.</span> Se a operação depende de uma integração do sistema antigo, a implantação avalia o seu caso antes da proposta.</span>
            <span class="s-foot">Slide 7, revisado</span>
          </div>
          <span class="note-tag">Trecho fictício</span>
          <div class="who-row"><span class="who-chip"><b>Preparou</b> time MATA</span><span class="who-chip"><b>Usou</b> vendas</span></div>
        </div>
      </section>

      <section class="moment" aria-labelledby="m5">
        <h3 class="m-label" id="m5"><span><b>5</b>Depois da reunião</span></h3>
        <div class="cell before" data-label="Antes da MATA">
          <p>Ninguém volta para saber se a resposta ajudou. Na reunião seguinte, a mesma dúvida aparece.</p>
          <div class="who-row"><span class="who-chip"><b>Cobrou</b> você</span></div>
          <span class="desk">Na sua mesa: cobrar quem deveria ter mudado o slide</span>
        </div>
        <div class="node" aria-hidden="true"></div>
        <div class="cell with" data-label="Com a MATA">
          <p>A resposta foi útil para o comprador? O time volta a vendas antes de levar a explicação para o site.</p>
          <div class="artifact">
            <div class="a-top"><span>Retorno de vendas</span><span>Fictício</span></div>
            <dl>
              <div><dt>O que funcionou</dt><dd>O comprador entendeu as condições da troca.</dd></div>
              <div><dt>Nova pergunta</dt><dd><span class="hl">Quem prepara a equipe para a implantação?</span></dd></div>
              <div><dt>Próximo passo</dt><dd>Entra na próxima revisão, junto com o trecho do site.</dd></div>
            </dl>
          </div>
          <div class="who-row"><span class="who-chip"><b>Voltou</b> time MATA</span></div>
        </div>
      </section>

      <section class="moment totals" aria-labelledby="m6">
        <h3 class="m-label" id="m6"><span><b>=</b>Somando a semana</span></h3>
        <div class="cell before" data-label="Antes da MATA">
          <div class="big"><b>3</b><span>vezes a pergunta voltou para você: para explicar, decidir e cobrar.</span></div>
        </div>
        <div class="node" aria-hidden="true"></div>
        <div class="cell with" data-label="Com a MATA">
          <div class="big"><b>1</b><span>vez pedimos a sua palavra: para aprovar a nova ordem da semana.</span></div>
        </div>
      </section>

      <div class="takeaway">
        <p>Com essa decisão, quem vende tem uma resposta que consegue sustentar, quem cuida do site sabe o que precisa rever e você sabe por que o post mudou de data.</p>
        <div>
          {more(L('mecanismos'), 'Ver o shadowing, o RPM e os outros mecanismos da MATA')}
          <details class="read-alt">
            <summary>Ler a cena em texto corrido<span class="plus" aria-hidden="true"></span></summary>
            <div class="body"><p>No shadowing comercial, alguém da MATA ouve a pergunta junto com o vendedor. A IA ajuda a localizar o que já está documentado, e o nosso time confere com quem cuida da implantação em quais casos a resposta muda. Aí entra o RPM, nosso ranking de prioridades. Podemos recomendar que a apresentação de amanhã explique essa diferença e que o próximo post espere. Vendas usa a nova versão, nós voltamos para saber se o comprador conseguiu avançar.</p></div>
          </details>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="band surface" aria-labelledby="h-exemplo">
  <div class="wrap case">
    <div>
      <p class="label">Software para saúde</p>
      <h2 id="h-exemplo">Um exemplo de quem já trabalhou assim</h2>
      <p class="lead" style="margin-top:18px">Uma empresa de software para saúde, com 25 anos de mercado, precisava reapresentar seu portfólio. Nos três primeiros meses de um plano de doze, a nova posição já estava no site, nos canais da empresa e no lançamento em um evento do setor.</p>
      {more(L('resultados'), 'Ver resultados da MATA')}
    </div>
    <figure style="margin:0" aria-label="Três primeiros meses de um plano de doze">
      <div class="months" aria-hidden="true">{''.join('<i class="on"></i>' if i < 3 else '<i></i>' for i in range(12))}</div>
      <div class="months-legend" aria-hidden="true"><span>Mês 1</span><span>Mês 12</span></div>
      <div class="facts"><span class="fact">Site</span><span class="fact">Canais da empresa</span><span class="fact">Lançamento em evento do setor</span></div>
    </figure>
  </div>
</section>

<section class="band forest" aria-labelledby="h-mudou">
  <div class="blob" aria-hidden="true"></div>
  <div class="wrap">
    <div class="measure">
      <h2 id="h-mudou">Quando a empresa mudou mais do que a marca</h2>
      <p class="lead" style="margin-top:20px">Às vezes já existe um time, mas o site ainda descreve o primeiro produto e a apresentação já não faz justiça ao que a empresa sabe fazer. A MATA também conduz reposicionamentos e acompanha a mudança naquilo que as pessoas leem, ouvem e usam para comprar.</p>
      {more(L('reposicionamento-de-marca'), 'Conhecer o trabalho de reposicionamento')}
    </div>
  </div>
</section>

<section class="band" aria-labelledby="h-contratar">
  <div class="wrap">
    <div class="head">
      <h2 id="h-contratar">Como contratar</h2>
      <p class="lead">Você escolhe uma assinatura mensal ou anual. Combinamos a dedicação do time por mês e, se fizer sentido, a produção do MATA AI Lab. Para conhecer o valor, conte um pouco sobre sua empresa.</p>
    </div>
    <div class="layers">
      <div class="layer team"><span class="tag">Mensal ou anual</span><h3>Time MATA</h3><p>As horas são do time como um todo.</p></div>
      <div class="layer lab"><span class="tag">Opcional</span><h3>MATA AI Lab</h3><p>Produções com direção humana e inteligência artificial.</p></div>
      <div class="layer spec"><span class="tag">Orçamento separado</span><h3>Projetos com especialistas</h3><p>Uma filmagem presencial ou um desenvolvimento mais complexo.</p></div>
    </div>
    <div class="actions" style="margin-top:28px">
      <a class="btn" href="{L('assinatura')}">Entender a assinatura <span class="arr" aria-hidden="true">→</span></a>
      <a class="btn line" href="{L('contato')}">Conversar sobre valores</a>
    </div>
  </div>
</section>

<section class="band surface" aria-labelledby="h-blog-home">
  <div class="wrap split">
    <div>
      <h2 id="h-blog-home">No blog da MATA</h2>
      <p class="lead" style="margin-top:18px">Por onde começar quando a empresa já vende bem, mas ainda depende de quem a fundou para tocar o marketing? Nosso guia mostra como escolher a primeira prioridade, quem pode decidir e o que observar nos primeiros 90 dias.</p>
    </div>
    <a class="read" href="{L('blog-como-estruturar-a-area-de-marketing')}">
      <span class="by">Por Time da MATA</span>
      <h3>Como estruturar a área de marketing quando a empresa já cresceu</h3>
      <span class="more" style="justify-self:start">Ler o guia para estruturar marketing <span aria-hidden="true">→</span></span>
    </a>
  </div>
</section>
'''


def page_como_funciona(L):
    steps = [
        ("Começamos por uma conversa real.", "Sentamos com a liderança, ouvimos o comercial e olhamos o que um comprador recebe hoje. Uma proposta recente às vezes ensina mais sobre a marca do que uma apresentação institucional."),
        ("Montamos o time para o trabalho que existe.", "Identificamos quem já cuida de cada assunto e combinamos a dedicação de que a empresa precisa, inclusive quando ela já tem profissionais ou parceiros."),
        ("Definimos quem decide o quê.", "Você sabe quem conduz o dia a dia, quais escolhas o time pode fazer e em que momento vai precisar da sua palavra."),
        ("Reunimos o conhecimento da marca.", "Organizamos informações de produto, materiais aprovados e decisões num lugar combinado com a empresa. A IA ajuda a localizar e comparar essas referências quando aparece uma demanda."),
        ("Chegamos com as prioridades da semana.", "Propomos uma ordem e explicamos o motivo. Se um lançamento passar na frente de outra iniciativa, fica claro o que vai mudar de data."),
        ("Levamos o trabalho até o uso.", "Nosso time prepara, revisa e acompanha a execução com as pessoas envolvidas. Você pode ver o que está em andamento e como a dedicação do mês foi distribuída."),
        ("Voltamos a quem usou.", "O vendedor conseguiu explicar o produto com o novo material? A dúvida que continuou aparecendo volta para a equipe, com alguém responsável por investigar e corrigir."),
    ]
    items = "".join(f"<li><div><h3>{t}</h3><p>{p}</p></div></li>" for t, p in steps)
    return f'''
<section class="page-hero" aria-labelledby="h-cf">
  <div class="wrap">
    <h1 id="h-cf">Como a MATA assume o marketing da sua empresa</h1>
    <p class="lead">Você tem um time de marketing que participa das conversas de negócio, recomenda onde concentrar o esforço e responde pelo que foi combinado. Para começar, precisamos conhecer o que sua empresa vende e ouvir quem já está perto dos clientes.</p>
  </div>
</section>
<section class="band surface" aria-labelledby="h-entramos">
  <div class="wrap">
    <div class="head"><h2 id="h-entramos">O que acontece quando entramos</h2></div>
    <ol class="steps">{items}</ol>
    {more(L('mecanismos'), 'Ver o que acontece numa semana com a MATA')}
  </div>
</section>
<section class="band" aria-labelledby="h-tec">
  <div class="wrap split">
    <div>
      <h2 id="h-tec">Onde entra a tecnologia?</h2>
      <p class="lead" style="margin-top:20px">Na MATA, pessoas e inteligência artificial trabalham com as mesmas referências da marca. Se duas apresentações descrevem o mesmo produto de jeitos diferentes, a IA pode encontrar as versões e apontar a diferença. Uma pessoa conversa com produto, decide qual informação vale e confere onde a correção precisa aparecer. É assim que usamos tecnologia no marketing, inclusive nos meses em que a empresa não encomenda uma produção do AI Lab.</p>
    </div>
    <div class="mem" aria-hidden="true" style="max-width:440px">
      <div class="ai"><small>Inteligência artificial</small>Encontra as versões e aponta a diferença.</div>
      <div class="glass"></div>
      <div class="person"><small>Uma pessoa do time</small>Conversa com produto, decide qual informação vale e confere onde a correção precisa aparecer.</div>
    </div>
  </div>
</section>
<section class="band forest" aria-labelledby="h-continua">
  <div class="blob" aria-hidden="true"></div>
  <div class="wrap measure" style="margin-left:auto;margin-right:auto">
    <h2 id="h-continua">O que continua com a sua empresa?</h2>
    <p class="lead" style="margin-top:20px">Decisões como entrar num mercado, mudar um produto ou aprovar um investimento continuam com quem responde pelo negócio. Quando o marketing depende de uma delas, chegamos com a questão, nossa recomendação e o que muda se a escolha for outra.</p>
  </div>
</section>
<section class="band surface" aria-labelledby="h-duvidas">
  <div class="wrap">
    <div class="head"><h2 id="h-duvidas">Dúvidas sobre o time</h2></div>
    <div class="qa">
      <div><h3>Qual é a diferença entre a MATA e uma agência?</h3><p>Na MATA, você contrata o próprio time que conduz o marketing no dia a dia. Ele participa das conversas da empresa, identifica o que merece atenção e responde pela sequência do trabalho, inclusive quando a próxima decisão ainda não virou um pedido.</p></div>
      <div><h3>É possível estruturar o marketing sem contratar funcionários?</h3><p>Sim. A assinatura permite reunir as competências de que sua empresa precisa e definir uma dedicação mensal para elas. Sua equipe participa com o conhecimento de produto, o retorno das vendas e as decisões que cabem ao negócio.</p></div>
      <div><h3>Como um time de marketing externo consegue trabalhar por dentro?</h3><p>Com acesso às pessoas certas e ao trabalho como ele acontece. Combinamos de quais reuniões participar, onde consultar as informações da marca e quem pode aprovar cada mudança. Se a sua empresa já tem um time, definimos juntos que responsabilidade a MATA vai assumir.</p></div>
    </div>
    <div class="links">{more(L('assinatura'), 'Ver as modalidades de assinatura')}</div>
  </div>
</section>
'''


def page_assinatura(L):
    def scale(team, lab):
        dots = lambda n: "".join('<i class="on"></i>' if i < n else "<i></i>" for i in range(3))
        return (f'<div class="scale-row" aria-hidden="true"><span class="scale">{dots(team)} dedicação do time</span>'
                f'<span class="scale">{dots(lab)} produção do Lab</span></div>')
    return f'''
<section class="page-hero gradient" aria-labelledby="h-as">
  <div class="wrap">
    <h1 id="h-as">Como funciona a assinatura da MATA</h1>
    <p class="lead">Sua empresa contrata uma dedicação mensal do Time MATA. Essas horas dão espaço para conhecer o negócio, participar das decisões e fazer o trabalho que vocês escolheram como prioridade. O valor depende da configuração, que definimos com você numa conversa.</p>
    <div class="actions"><a class="btn" href="{L('contato')}">Conversar sobre a minha assinatura <span class="arr" aria-hidden="true">→</span></a></div>
  </div>
</section>

<form id="assinatura-pref" onsubmit="return false">
<section class="band" aria-labelledby="h-modalidade">
  <div class="wrap">
    <div class="head"><h2 id="h-modalidade">Mensal ou anual?</h2></div>
    <fieldset style="border:0;margin:0;padding:0;min-width:0">
      <legend class="sr">Modalidade</legend>
      <div class="modes">
        <label class="pick"><input type="radio" name="modalidade" value="Mensal" id="mod-mensal"><span class="pk-top"><h3>Mensal</h3><span class="ring" aria-hidden="true"></span></span><p>Você contrata a dedicação do time em ciclos mensais, sem assumir um compromisso anual.</p></label>
        <label class="pick"><input type="radio" name="modalidade" value="Anual" id="mod-anual"><span class="pk-top"><h3>Anual</h3><span class="ring" aria-hidden="true"></span></span><p>Você assume um compromisso de doze meses, com uma dedicação do time definida para cada mês.</p></label>
      </div>
      <div class="unsure"><label class="chip"><input type="radio" name="modalidade" value="Não sei ainda" id="mod-nao-sei">Não sei ainda</label></div>
    </fieldset>
    <p class="measure" style="margin-top:24px">Nas duas modalidades, revemos as prioridades com você ao longo do trabalho. A proposta apresenta o valor e as condições para a sua empresa.</p>
  </div>
</section>

<section class="band surface" aria-labelledby="h-combinar">
  <div class="wrap">
    <div class="head"><h2 id="h-combinar">O que você pode combinar na assinatura</h2></div>
    <div class="sub-grid">
      <div class="layer-stack">
        <article class="L team" aria-labelledby="h-time">
          <div class="L-top"><h3 id="h-time">Time MATA</h3><span class="tag">Dedicação mensal</span></div>
          <p>As horas são do time como um todo. Uma reunião com vendas, o planejamento da semana e a revisão de uma página usam parte da dedicação mensal. Você acompanha o que ocupou o time e o que ainda cabe no mês.</p>
        </article>
        <article class="L lab" aria-labelledby="h-lab">
          <div class="L-top"><h3 id="h-lab">MATA AI Lab</h3><span class="tag">Opcional</span></div>
          <p>Você pode acrescentar produções com direção humana e inteligência artificial, como um vídeo de animação. Antes de começar, combinamos o que será produzido, o formato, as revisões e quantas unidades do Lab aquele trabalho utiliza. A produção e as revisões previstas usam essas unidades, separadas das horas do time.</p>
          <fieldset style="border:0;margin:0;padding:0;min-width:0">
            <legend class="sr">MATA AI Lab</legend>
            <div class="unsure" style="margin-top:4px">
              <label class="chip"><input type="radio" name="lab" value="Quero incluir" id="lab-sim">Quero incluir</label>
              <label class="chip"><input type="radio" name="lab" value="Agora não" id="lab-nao">Agora não</label>
              <label class="chip"><input type="radio" name="lab" value="Não sei ainda" id="lab-nao-sei">Não sei ainda</label>
            </div>
          </fieldset>
        </article>
        <article class="L spec" aria-labelledby="h-esp">
          <div class="L-top"><h3 id="h-esp">Projetos com especialistas</h3><span class="tag">Orçamento separado</span></div>
          <p>Uma filmagem presencial ou um desenvolvimento mais complexo pode pedir profissionais e recursos específicos. A MATA organiza o projeto e apresenta um orçamento separado, que você avalia antes de seguir.</p>
          <label class="check"><input type="checkbox" name="especialistas" value="Tenho um projeto em mente" id="esp">Tenho um projeto em mente</label>
        </article>

        <div style="margin-top:clamp(28px,4vw,48px)">
          <h2 id="h-comecar">Por onde começar?</h2>
          <p class="lead" style="margin:18px 0 22px">Starter, Growth e Pro são pontos de partida para combinar a dedicação do time e a quantidade de produção do Lab. A forma de trabalhar é a mesma. Se a sua empresa precisar de outra combinação, conversamos sobre uma proposta sob medida.</p>
          <fieldset style="border:0;margin:0;padding:0;min-width:0" aria-labelledby="h-comecar">
            <div class="starts">
              <label class="pick"><input type="radio" name="ponto" value="Starter" id="pt-starter"><span class="pk-top"><h3>Starter</h3><span class="ring" aria-hidden="true"></span></span>{scale(1, 1)}</label>
              <label class="pick"><input type="radio" name="ponto" value="Growth" id="pt-growth"><span class="pk-top"><h3>Growth</h3><span class="ring" aria-hidden="true"></span></span>{scale(2, 2)}</label>
              <label class="pick"><input type="radio" name="ponto" value="Pro" id="pt-pro"><span class="pk-top"><h3>Pro</h3><span class="ring" aria-hidden="true"></span></span>{scale(3, 3)}</label>
            </div>
            <div class="unsure">
              <label class="chip"><input type="radio" name="ponto" value="Sob medida" id="pt-medida">Sob medida</label>
              <label class="chip"><input type="radio" name="ponto" value="Me ajudem a escolher" id="pt-ajuda">Me ajudem a escolher</label>
            </div>
          </fieldset>
          <div class="links">{more(L('contato'), 'Me ajudem a escolher')}</div>
        </div>
      </div>

      <aside class="summary" aria-labelledby="h-resumo">
        <h3 id="h-resumo">Para a nossa conversa</h3>
        <dl>
          <div><dt>Modalidade</dt><dd data-sum="modalidade" data-empty="Não sei ainda">Não sei ainda</dd></div>
          <div><dt>Ponto de partida</dt><dd data-sum="ponto" data-empty="Não sei ainda">Não sei ainda</dd></div>
          <div><dt>MATA AI Lab</dt><dd data-sum="lab" data-empty="Não sei ainda">Não sei ainda</dd></div>
          <div><dt>Especialistas</dt><dd data-sum="especialistas" data-empty="Nenhum projeto agora">Nenhum projeto agora</dd></div>
        </dl>
        <p>A proposta apresenta o valor e as condições para a sua empresa.</p>
        <a class="btn" href="{L('contato')}">Conversar sobre a minha assinatura</a>
        <a class="btn line" href="{L('contato')}">Quero receber uma proposta</a>
      </aside>
    </div>
  </div>
</section>
</form>

<section class="band" aria-labelledby="h-acompanhar">
  <div class="wrap">
    <div class="head">
      <h2 id="h-acompanhar">Como acompanhar o mês?</h2>
      <p class="lead">Você pode acompanhar a dedicação por semana e por tema, como apoio a vendas, marca e planejamento. O RPM, nosso ranking de prioridades, mostra o que propomos fazer em seguida e por quê. Se surgir uma urgência, olhamos juntos para o tempo disponível e decidimos o que pode esperar.</p>
    </div>
    <div class="track">
      <div class="panel">
        <span class="demo-tag">Exemplo ilustrativo</span>
        <p class="label" style="margin:0">Dedicação da semana por tema</p>
        <div class="theme-bar" aria-hidden="true"><i style="width:46%"></i><i style="width:32%"></i><i style="width:22%"></i></div>
        <div class="legend"><span><i style="background:var(--forest)"></i>Apoio a vendas</span><span><i style="background:#7FA79B"></i>Marca</span><span><i style="background:var(--lavender)"></i>Planejamento</span></div>
      </div>
      <div class="panel">
        <span class="demo-tag">Exemplo ilustrativo</span>
        <p class="label" style="margin:0">RPM da semana</p>
        <ol class="ranked">
          <li>Corrigir a explicação na apresentação que vai para o comprador amanhã.</li>
          <li>Rever o mesmo trecho no site com a pessoa que cuida da implantação.</li>
          <li>Retomar o conteúdo previsto depois dessas duas mudanças.</li>
        </ol>
      </div>
    </div>
    <div class="qa" style="margin-top:clamp(40px,5vw,64px)">
      <div><h3>Preciso saber quantas horas contratar?</h3><p>Pode chegar com uma situação. Conte quem cuida do marketing hoje, o que já está em andamento e o que está esperando alguém assumir. A gente usa esse contexto para recomendar um ponto de partida.</p></div>
      <div><h3>Preciso contratar o AI Lab para ter IA no meu marketing?</h3><p>O time já usa IA na rotina da sua marca. Você escolhe o Lab quando quiser incluir produções finalizadas com escopo próprio.</p></div>
      <div><h3>Quanto custa a MATA?</h3><p>O valor considera a dedicação mensal do time e as produções do Lab que você escolher. Depois de entender o que sua empresa precisa, apresentamos a configuração e o valor na proposta.</p></div>
    </div>
    <div class="links">
      {more(L('contato'), 'Quero receber uma proposta')}
      {more(L('mecanismos'), 'Ver uma semana com a MATA')}
    </div>
  </div>
</section>
'''


def page_mecanismos(L):
    return f'''
<section class="page-hero" aria-labelledby="h-me">
  <div class="wrap">
    <h1 id="h-me">Uma semana com a MATA</h1>
    <p class="lead">Como o que se ouve numa reunião de vendas vira uma decisão de marketing? Acompanhe um exemplo. Um comprador quer trocar um sistema e pergunta se precisará interromper a operação. Quem vende sabe responder, mas precisa dar a mesma explicação em toda reunião.</p>
  </div>
</section>
<div class="band surface tight">
  <div class="wrap">
    <div class="week">
      <section aria-labelledby="w1">
        <div class="when"><b>Shadowing comercial</b></div>
        <div><h2 id="w1">A pergunta aparece no shadowing comercial</h2>
          <p>Alguém da MATA acompanha a conversa para ouvir o que o comprador pergunta, que exemplo o vendedor usa e em que ponto aparece a dúvida. Do shadowing sai uma observação que dá para investigar. Nesse exemplo, a apresentação explica de que depende a transição de um sistema para outro?</p></div>
      </section>
      <section aria-labelledby="w2">
        <div class="when"><b>Memória da marca</b><span>SSOT e Brand OS</span></div>
        <div><h2 id="w2">A resposta entra na memória da marca</h2>
          <p>Em uma conversa de perguntas e respostas com quem implanta o produto, conferimos o que a empresa pode prometer. Registramos a explicação e a sua origem na base de conhecimento da marca. É a nossa fonte comum de consulta, também chamada de SSOT. O Brand OS reúne as orientações sobre como aquela marca fala, se apresenta e aplica suas escolhas.</p>
          <p>Na prática, a IA pode buscar a explicação que produto validou, enquanto a pessoa que escreve confere se ela faz sentido para quem está comprando. Quando a resposta muda, sabemos onde voltar.</p></div>
      </section>
      <section aria-labelledby="w3">
        <div class="when"><b>RPM</b><span>Ranking de Prioridades da MATA</span></div>
        <div><h2 id="w3">O RPM mostra o que vale fazer primeiro</h2>
          <p>No Ranking de Prioridades da MATA, propomos à empresa uma ordem de trabalho e explicamos o motivo. Nesse caso, a apresentação que vendas vai usar amanhã pode passar na frente de um conteúdo já previsto. Você consegue ver tanto o que entrou como o que vai esperar.</p>
          <p class="ranked-cap">Como a proposta de ordem pode aparecer</p>
          <ol class="ranked">
            <li>Corrigir a explicação na apresentação que vai para o comprador amanhã.</li>
            <li>Rever o mesmo trecho no site com a pessoa que cuida da implantação.</li>
            <li>Retomar o conteúdo previsto depois dessas duas mudanças.</li>
          </ol></div>
      </section>
      <section aria-labelledby="w4">
        <div class="when"><b>Weekly e sprint</b></div>
        <div><h2 id="w4">O sprint leva a escolha para a semana</h2>
          <p>Na conversa semanal, a weekly, conferimos se apareceu algo que mude a ordem. O sprint é a parte do ranking que cabe no período, com responsáveis e dependências. Uma correção pode estar pronta para vendas enquanto a página ainda espera a validação de produto, e essa diferença fica visível.</p></div>
      </section>
      <section aria-labelledby="w5">
        <div class="when"><b>CPM</b><span>Processo de conteúdo e matriz de conteúdo</span></div>
        <div><h2 id="w5">O processo de conteúdo começa pelo que vale dizer</h2>
          <p>No CPM, o processo de conteúdo da MATA, escolhemos primeiro o ângulo, ou seja, qual pergunta vale responder e para quem. Só então escolhemos o formato. A mesma dúvida pode pedir um exemplo curto na proposta e uma explicação mais detalhada no site. A matriz de conteúdo registra esses desdobramentos e o que ainda precisa de aprovação.</p></div>
      </section>
      <section aria-labelledby="w6">
        <div class="when"><b>Depois da entrega</b><span>Working session e acompanhamento das horas</span></div>
        <div><h2 id="w6">O que acontece depois da entrega?</h2>
          <p>Voltamos a quem usou o material. Se o comprador entendeu as condições da troca, mas agora precisa saber quem prepara a equipe para a implantação, temos uma pergunta melhor para a próxima revisão. No acompanhamento das horas, a empresa também vê quanto da dedicação foi para apoio a vendas e o que ainda cabe no mês.</p>
          <p>Quando uma decisão pede mais tempo junto, fazemos uma sessão de trabalho, a working session. Podemos abrir as versões de uma página com o time, comparar como cada uma responde à dúvida do comprador e sair com a alteração escolhida. Os rituais acompanham o que a marca precisa resolver.</p></div>
      </section>
    </div>
    <div class="links">
      {more(L('assinatura'), 'Ver como contratar essa rotina')}
      {more(L('blog-pensar-no-sistema'), 'Como escolhemos o que vale transformar em processo')}
    </div>
  </div>
</div>
'''


def page_reposicionamento(L):
    return f'''
<section class="page-hero" aria-labelledby="h-rp">
  <div class="wrap">
    <h1 id="h-rp">Reposicionamento de marca para empresas que já mudaram</h1>
    <p class="lead">Quando a empresa passa a resolver problemas maiores, é comum o comercial aprender a explicar isso antes da marca. Quem já é cliente conhece o negócio de hoje, quem chega pelo site ainda encontra a empresa de alguns anos atrás.</p>
    <p class="lead">A MATA ajuda a entender essa distância, definir como a marca deve se apresentar e levar a mudança até os materiais que participam da compra.</p>
  </div>
</section>
<div class="band surface tight">
  <div class="wrap">
    <div class="week">
      <section aria-labelledby="r1"><div class="when"><b>1</b></div><div><h2 id="r1">O que o mercado já reconhece na sua empresa?</h2>
        <p>Começamos com quem conhece lados diferentes do negócio. A liderança conta o que mudou, o comercial traz as perguntas que recebe e os clientes mostram o que pesou na escolha. Essa investigação revela o que precisa mudar e o que vale preservar, inclusive quando as respostas surpreendem quem fundou a marca.</p></div></section>
      <section aria-labelledby="r2"><div class="when"><b>2</b></div><div><h2 id="r2">Que promessa a empresa consegue sustentar?</h2>
        <p>Comparamos essas percepções com o que a empresa de fato entrega. A partir daí, definimos para quem a marca é mais relevante, como explicar seu valor e que provas acompanham essa explicação. Essas escolhas orientam o jeito de escrever e a identidade visual.</p></div></section>
      <section aria-labelledby="r3"><div class="when"><b>3</b></div><div><h2 id="r3">Onde a nova marca precisa aparecer primeiro?</h2>
        <p>Pode ser na proposta que sai amanhã, na demonstração do produto ou no site. Escolhemos uma aplicação que as pessoas realmente usam e testamos se a nova direção funciona ali. Se vendas precisa explicar com as próprias palavras o que a apresentação quis dizer, ainda há trabalho.</p>
        <p>A implantação e o acompanhamento podem continuar com o time MATA incorporado à operação, conforme o escopo combinado.</p></div></section>
    </div>
    <div class="actions" style="margin-top:32px">
      <a class="btn line" href="{L('resultados')}">Ver um reposicionamento na prática</a>
      <a class="btn" href="{L('contato')}">Conversar sobre a nossa marca <span class="arr" aria-hidden="true">→</span></a>
    </div>
    <div class="links">{more(L('blog-como-implementar-o-reposicionamento-de-marca'), 'O que muda na proposta comercial depois do reposicionamento?')}</div>
  </div>
</div>
'''


def page_resultados(L):
    cases = [
        ("Software para saúde", "3 de 12", "meses até a nova posição chegar ao mercado",
         "Uma empresa com 25 anos de mercado precisava reposicionar e relançar seu portfólio. Nos três primeiros meses de um plano de doze, a nova posição chegou ao site, aos canais da empresa e a um evento do setor, onde o portfólio foi apresentado ao mercado."),
        ("Tecnologia financeira", "35", "inserções em dois meses e meio",
         "O relacionamento com a imprensa entrou na rotina de marketing da fintech. Em dois meses e meio, foram 35 inserções, entre elas uma participação em TV em horário nobre."),
        ("Mercado imobiliário", "1 mês", "para reorganizar a aquisição de clientes",
         "Em uma incorporadora de alto padrão em São Paulo, a MATA trabalhou na reorganização de todo o processo de aquisição de clientes. A reestruturação foi feita em um mês."),
        ("Grupo de empresas de ingredientes", "3", "marcas no mesmo grupo",
         "Três marcas do mesmo grupo precisavam explicar o próprio papel. A MATA desenvolveu o posicionamento e a narrativa de cada uma, preservando as diferenças entre elas e a relação que mantêm dentro do grupo."),
        ("Marca de barras de proteína", "100 mil", "visualizações orgânicas nas duas primeiras semanas",
         "A MATA participou da criação da marca desde o início, do posicionamento à abertura dos canais. Nas duas primeiras semanas, o conteúdo ultrapassou 100 mil visualizações orgânicas, sem investimento em mídia paga nesse período."),
    ]
    arts = "".join(
        f'<article aria-labelledby="c{i}"><div class="fig" aria-hidden="true">{fig}<small>{cap}</small></div>'
        f'<div><h2 id="c{i}">{t}</h2><p>{p}</p></div></article>'
        for i, (t, fig, cap, p) in enumerate(cases))
    return f'''
<section class="page-hero" aria-labelledby="h-rs">
  <div class="wrap">
    <h1 id="h-rs">O que as marcas colocaram em prática com a MATA</h1>
    <p class="lead">Uma empresa precisava reapresentar um portfólio inteiro, outra precisava dar uma voz própria a três marcas do mesmo grupo. O trabalho começou por questões bem diferentes, como mostram estes cinco exemplos.</p>
  </div>
</section>
<div class="band surface tight">
  <div class="wrap">
    <div class="cases">{arts}</div>
    <div class="links">{more(L('como-funciona'), 'Ver como a MATA trabalha')}</div>
  </div>
</div>
'''


def page_sobre(L):
    return f'''
<section class="page-hero" aria-labelledby="h-so">
  <div class="wrap split">
    <div>
      <h1 id="h-so">A MATA nasceu de uma pergunta sobre quem cuida do marketing</h1>
    </div>
    <div>
      <p class="lead">Caroline Miranda Martha tem mais de 13 anos de experiência em marketing e comunicação, em empresas globais e em funções locais e internacionais. Uma situação se repetia, mesmo quando havia gente muito boa fazendo cada parte do trabalho. Alguém dentro da empresa ainda precisava juntar o que vendas sabia, o que produto tinha mudado e o que a marca dizia ao mercado.</p>
      <p>Caroline fundou a MATA para assumir esse trabalho junto com as empresas. Somos uma martech, uma empresa de marketing e tecnologia. Reunimos gente com experiência para conduzir a marca e inteligência artificial para organizar o conhecimento de que esse time precisa, semana após semana.</p>
    </div>
  </div>
</section>
<section class="band surface" aria-labelledby="h-porque">
  <div class="wrap split" style="align-items:center">
    <div>
      <h2 id="h-porque">Por que MATA?</h2>
      <p class="lead" style="margin-top:20px">O nome vem de uma observação da natureza. Numa mata, organismos diferentes crescem em relação uns com os outros. Foi daí que veio a ideia de formar um time com identidade própria que pudesse fazer parte de outra empresa, aprendendo com ela e contribuindo com o que ela precisa para crescer.</p>
    </div>
    <div class="organic" aria-hidden="true"><div class="blob"></div></div>
  </div>
</section>
<section class="band" id="principios" aria-labelledby="h-princ">
  <div class="wrap">
    <div class="head"><h2 id="h-princ">Princípios da MATA</h2></div>
    <div class="principles">
      <div class="panel"><p><strong>O negócio é o briefing.</strong> Se uma página está difícil de entender, gostamos de ouvir alguém explicar o produto a um comprador antes de começar a reescrever.</p></div>
      <div class="panel"><p><strong>Quem vê um problema pode trazê-lo para a conversa.</strong> Isso vale inclusive para revisar o trabalho de quem tem mais experiência. Uma boa observação sobre o que dificulta a vida do cliente pesa mais do que quem assinou a primeira versão.</p></div>
      <div class="panel"><p><strong>Aprendemos trabalhando juntos.</strong> Numa sessão de trabalho, abrimos o material, discutimos uma escolha e testamos outra. Quando descobrimos um jeito melhor de fazer algo que se repete, registramos o que mudou para a próxima pessoa conseguir usar.</p></div>
      <div class="panel"><p><strong>Voltamos para saber como foi.</strong> Quem cuidou de uma apresentação também tem interesse em ouvir o vendedor depois da reunião. Esse retorno pode mudar a próxima versão, a prioridade da semana ou a pergunta que faremos a produto.</p></div>
    </div>
    <div class="links">
      {more(LINKEDIN_CAROL, 'Conhecer Caroline no LinkedIn')}
      {more(L('mecanismos'), 'Ver os rituais da MATA')}
      {more(L('blog-produzir-marketing-nao-e-conduzir-marketing'), 'Ler a reflexão da Caroline sobre produzir e conduzir marketing')}
    </div>
  </div>
</section>
'''


def page_blog(L):
    def card(key, title, dek, by):
        return (f'<a class="read" href="{L(key)}"><span class="by">{by}</span><h3>{title}</h3><p>{dek}</p></a>')
    return f'''
<section class="page-hero" aria-labelledby="h-bl">
  <div class="wrap">
    <h1 id="h-bl">Blog da MATA</h1>
    <p class="lead">O que fazer quando a empresa já cresceu, mas o marketing ainda depende de quem a fundou? Escrevemos sobre as decisões que aparecem nessa fase, com guias do time e artigos de Caroline Miranda Martha sobre marca, tecnologia e o trabalho de conduzir marketing.</p>
  </div>
</section>
<div class="band surface tight">
  <div class="wrap stack" style="--gap:clamp(36px,5vw,56px)">
    <section aria-labelledby="g1"><h2 id="g1" style="margin-bottom:20px">Para quem está montando o marketing</h2>
      <div class="reads">{card('blog-como-estruturar-a-area-de-marketing', 'Como estruturar a área de marketing quando a empresa já cresceu', 'Antes de abrir a primeira vaga, decida o que essa pessoa precisará resolver. Um guia para definir responsabilidades, comparar estruturas e organizar os primeiros 90 dias.', 'Por Time da MATA')}</div></section>
    <section aria-labelledby="g2"><h2 id="g2" style="margin-bottom:20px">Para quem está mudando a marca</h2>
      <div class="reads">{card('blog-como-implementar-o-reposicionamento-de-marca', 'O que muda na próxima proposta depois do reposicionamento da marca?', 'A proposta que sai amanhã é um bom lugar para descobrir se a nova marca já ajuda alguém a vender.', 'Por Caroline Miranda Martha')}</div></section>
    <section aria-labelledby="g3"><h2 id="g3" style="margin-bottom:20px">Para quem está repensando o trabalho com IA</h2>
      <div class="reads">{card('blog-produzir-marketing-nao-e-conduzir-marketing', 'Produzir marketing não é conduzir marketing', 'A apresentação ficou pronta em uma tarde, mas quem passou a semana juntando as informações? Uma reflexão sobre o trabalho que continua com a liderança quando produzir fica mais fácil.', 'Por Caroline Miranda Martha')}
      {card('blog-pensar-no-sistema', 'Finalmente pensar no sistema começou a compensar', 'Um grupo de produtos, uma conversa com o time e uma dúvida prática sobre quando vale preparar o trabalho para a próxima vez.', 'Por Caroline Miranda Martha')}</div></section>
  </div>
</div>
'''


def page_contato(L):
    return f'''
<section class="page-hero gradient" aria-labelledby="h-ct">
  <div class="wrap">
    <h1 id="h-ct">Conte o que está acontecendo com o marketing da sua empresa</h1>
    <p class="lead">Pode ser que ninguém tenha assumido o marketing ainda, que você esteja coordenando vários parceiros ou que a marca precise acompanhar uma mudança no negócio. Conte por onde gostaria de começar. Nosso time lê sua mensagem para conversar sobre o que a MATA poderia assumir e qual assinatura faria sentido.</p>
  </div>
</section>
<div class="band surface">
  <div class="wrap split">
    <form class="form" id="contato-form" novalidate
      data-required="Preencha este campo para enviar sua mensagem."
      data-email="Confira o endereço de e-mail, por exemplo, nome@empresa.com.br."
      data-sending="Enviando sua mensagem…"
      data-ok="Recebemos sua mensagem. O time MATA vai responder pelo e-mail que você informou."
      data-fail="Sua mensagem não foi enviada. Tente de novo ou escreva para {EMAIL}.">
      <div class="pref" id="pref-box" hidden>
        <p class="label" style="margin:0">Assinatura</p>
        <p id="pref-text"></p>
        <button type="button" class="x" id="pref-clear">Remover</button>
      </div>
      <input type="hidden" name="preferencia" id="pref-input">
      <div class="field"><label for="f-nome">Seu nome</label><input id="f-nome" name="nome" required autocomplete="name" aria-describedby="f-nome-err"><p class="err" id="f-nome-err" hidden></p></div>
      <div class="field"><label for="f-email">E-mail de trabalho</label><input id="f-email" name="email" type="email" required autocomplete="email" aria-describedby="f-email-err"><p class="err" id="f-email-err" hidden></p></div>
      <div class="field"><label for="f-empresa">Nome da empresa</label><input id="f-empresa" name="empresa" required autocomplete="organization" aria-describedby="f-empresa-err"><p class="err" id="f-empresa-err" hidden></p></div>
      <div class="field"><label for="f-msg">O que você gostaria que a MATA ajudasse a resolver?</label><p class="hint" id="f-msg-hint">Se estiver em dúvida sobre a assinatura, pode dizer quem cuida do marketing hoje e o que está ficando para depois.</p><textarea id="f-msg" name="mensagem" required aria-describedby="f-msg-hint f-msg-err"></textarea><p class="err" id="f-msg-err" hidden></p></div>
      <div><button class="btn" type="submit">Enviar mensagem</button></div>
      <p class="status" id="form-status" role="status" tabindex="-1" hidden></p>
    </form>
    <div>
      <p class="lead">Se preferir, escreva para <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </div>
  </div>
</div>
'''


def page_404(L):
    return f'''
<section class="page-hero" aria-labelledby="h-404">
  <div class="wrap">
    <h1 id="h-404">Não encontramos essa página.</h1>
    <p class="lead">Você pode voltar ao início ou ver como a MATA funciona.</p>
    <div class="actions"><a class="btn" href="{L('inicio')}">Voltar ao início</a><a class="btn line" href="{L('como-funciona')}">Como a MATA funciona</a></div>
  </div>
</section>
'''


# ---------------------------------------------------------------- blog a partir do pacote
def inline_md(text, L):
    text = esc(text)

    def link(m):
        label, href = m.group(1), html.unescape(m.group(2))
        if href.startswith("/pt"):
            return f'<a href="{L.from_path(href)}">{label}</a>'
        if href.startswith("mailto:"):
            return f'<a href="{href}">{label}</a>'
        return f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def parse_articles():
    raw = PACOTE.read_text()
    blocks = re.split(r"\n---\n", raw)
    found = {}
    for block in blocks:
        m = re.search(r"\*\*(Artigo do blog 0\d)", block)
        if not m:
            continue
        lines = block.strip().split("\n")
        start = next(i for i, ln in enumerate(lines) if ln.startswith("# "))
        found[m.group(1)] = lines[start:]
    return found


def render_article(lines, L, author_kind):
    title = lines[0][2:].strip()
    body = lines[1:]
    byline_raw = next(ln for ln in body if ln.startswith("Por "))
    body = body[body.index(byline_raw) + 1:]
    if author_kind == "caroline":
        byline = f'Por <a href="{L("sobre")}">Caroline Miranda Martha</a>, fundadora da MATA'
    else:
        byline = f'Por <a href="{L("inicio")}">Time da MATA</a>'

    out, para, i = [], [], 0
    in_summary = False
    related = []

    def flush():
        nonlocal para
        if para:
            text = " ".join(para)
            if re.fullmatch(r"\[[^\]]+\]\(/pt[^)]*\)", text):
                related.append(text)
            else:
                out.append(f"<p>{inline_md(text, L)}</p>")
            para = []

    while i < len(body):
        ln = body[i]
        if ln.startswith("## "):
            flush()
            if in_summary:
                out.append("</div>")
                in_summary = False
            name = ln[3:].strip()
            if name == "Resumo":
                out.append('<div class="summary-box">')
                in_summary = True
            out.append(f"<h2>{inline_md(name, L)}</h2>")
        elif ln.startswith("- "):
            flush()
            items = []
            while i < len(body) and body[i].startswith("- "):
                items.append(f"<li>{inline_md(body[i][2:], L)}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            if in_summary:
                out.append("</div>")
                in_summary = False
            continue
        elif ln.startswith("|"):
            flush()
            rows = []
            while i < len(body) and body[i].startswith("|"):
                rows.append([c.strip() for c in body[i].strip().strip("|").split("|")])
                i += 1
            head, data = rows[0], rows[2:]
            th = "".join(f'<th scope="col">{inline_md(c, L)}</th>' for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline_md(c, L)}</td>" for c in r) + "</tr>" for r in data)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        elif not ln.strip():
            flush()
        else:
            para.append(ln.strip())
        i += 1
    flush()
    if in_summary:
        out.append("</div>")
    rel_html = ""
    if related:
        links = []
        for r in related:
            m = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", r)
            links.append(more(L.from_path(m.group(2)), esc(m.group(1))))
        rel_html = '<div class="rel">' + "".join(links) + "</div>"
    main = f'''
<article>
  <header class="article-head gradient">
    <div class="wrap">
      <p class="label"><a href="{L('blog')}" style="color:inherit;text-decoration:none">Blog da MATA</a></p>
      <h1>{esc(title)}</h1>
      <p class="byline">{byline}</p>
    </div>
  </header>
  <div class="band surface tight">
    <div class="wrap">
      <div class="prose">
        {''.join(out)}
        {rel_html}
        <p class="back">{more(L('blog'), 'Voltar ao blog da MATA.')}</p>
      </div>
    </div>
  </div>
</article>
'''
    return title, main


# ---------------------------------------------------------------- documento
PAGES = {
    "inicio": page_inicio,
    "como-funciona": page_como_funciona,
    "assinatura": page_assinatura,
    "mecanismos": page_mecanismos,
    "reposicionamento-de-marca": page_reposicionamento,
    "resultados": page_resultados,
    "sobre": page_sobre,
    "blog": page_blog,
    "contato": page_contato,
    "404": page_404,
}


def jsonld(key):
    org = {"@type": "Organization", "@id": DOMAIN + "/#organizacao", "name": "MATA",
           "url": DOMAIN + "/pt", "email": EMAIL, "sameAs": [LINKEDIN_MATA],
           "founder": {"@type": "Person", "name": "Caroline Miranda Martha", "sameAs": [LINKEDIN_CAROL]}}
    if key == "inicio":
        data = dict(org, **{"@context": "https://schema.org", "description": ROUTES[key][2]})
    elif key.startswith("blog-"):
        author_kind = next(k for t, (r, k) in ARTICLES.items() if r == key)
        author = ({"@type": "Person", "name": "Caroline Miranda Martha", "url": DOMAIN + "/pt/sobre", "sameAs": [LINKEDIN_CAROL]}
                  if author_kind == "caroline" else {"@type": "Organization", "name": "Time da MATA", "url": DOMAIN + "/pt"})
        data = {"@context": "https://schema.org", "@type": "Article", "headline": ROUTES[key][1],
                "inLanguage": "pt-BR", "author": author, "publisher": {"@id": DOMAIN + "/#organizacao"},
                "mainEntityOfPage": DOMAIN + ROUTES[key][0]}
    else:
        return ""
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def meta_tags(key):
    path, title, desc, _ = ROUTES[key]
    canonical = DOMAIN + path
    tags = [f'<meta name="description" content="{esc(desc)}">']
    if key != "404":
        tags.append(f'<link rel="canonical" href="{canonical}">')
    else:
        tags.append('<meta name="robots" content="noindex">')
    tags += [f'<meta property="og:title" content="{esc(title)}">',
             f'<meta property="og:description" content="{esc(desc)}">',
             '<meta property="og:locale" content="pt_BR">',
             f'<meta property="og:type" content="{"article" if key.startswith("blog-") else "website"}">',
             f'<meta property="og:url" content="{canonical}">']
    return "\n".join(tags)


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def font_css(mode):
    faces = [("Stack Sans Headline", "stack-sans-headline"), ("Stack Sans Text", "stack-sans-text"), ("Stack Sans Notch", "stack-sans-notch")]
    out = []
    for fam, file in faces:
        src = (b64(ASSETS / "fontes" / f"{file}.woff2", "font/woff2") if mode == "preview"
               else f"/assets/fontes/{file}.woff2")
        out.append(f'@font-face{{font-family:"{fam}";src:url("{src}") format("woff2");font-weight:200 700;font-style:normal;font-display:swap}}')
    grad = b64(ASSETS / "mata-gradiente.webp", "image/webp") if mode == "preview" else "/assets/mata-gradiente.webp"
    out.append(f':root{{--grad:url("{grad}");--blob:url("{BLOB}")}}')
    return "\n".join(out)


def build_dist(articles):
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / "assets" / "fontes").mkdir(parents=True)
    L = Linker("dist")
    css = (SRC / "site.css").read_text()
    (dist / "assets" / "site.css").write_text(font_css("dist") + "\n" + css)
    shutil.copy(SRC / "site.js", dist / "assets" / "site.js")
    for f in (ASSETS / "fontes").glob("*.woff2"):
        shutil.copy(f, dist / "assets" / "fontes" / f.name)
    shutil.copy(ASSETS / "fontes" / "Befonts-License.txt", dist / "assets" / "fontes" / "LICENCA-Stack-Sans.txt")
    shutil.copy(ASSETS / "mata-gradiente.webp", dist / "assets" / "mata-gradiente.webp")

    bodies = {k: fn(L) for k, fn in PAGES.items()}
    for label, (key, kind) in ARTICLES.items():
        bodies[key] = render_article(articles[label], L, kind)[1]
    sitemap = []
    for key, main in bodies.items():
        path, title, desc, section = ROUTES[key]
        doc = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
{meta_tags(key)}
<link rel="preload" href="/assets/fontes/stack-sans-headline.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fontes/stack-sans-text.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{jsonld(key)}
</head>
<body>
{header(L, section)}
<main id="conteudo">
{main}
</main>
{footer(L)}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''
        target = dist / "404.html" if key == "404" else dist / path.lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc)
        if key != "404":
            sitemap.append(f"  <url><loc>{DOMAIN}{path}</loc></url>")
    (dist / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(sitemap) + "\n</urlset>\n")
    (dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    return bodies


def build_preview(articles):
    out = ROOT / "preview"
    out.mkdir(exist_ok=True)
    L = Linker("preview")
    css = font_css("preview") + "\n" + (SRC / "site.css").read_text()
    js = (SRC / "site.js").read_text()
    bodies = {k: fn(L) for k, fn in PAGES.items()}
    for label, (key, kind) in ARTICLES.items():
        bodies[key] = render_article(articles[label], L, kind)[1]
    views = []
    for key, main in bodies.items():
        _, title, desc, section = ROUTES[key]
        hidden = "" if key == "inicio" else " hidden"
        views.append(f'<main id="{"conteudo" if key == "inicio" else "v-" + key}" data-route="{key}" data-section="{section}" data-title="{esc(title)}" data-description="{esc(desc)}"{hidden}>\n{main}\n</main>')
    page = f'''<title>Novo site da MATA</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{esc(ROUTES['inicio'][2])}">
<style>
{css}
</style>
<script>document.documentElement.lang="pt-BR"</script>
<div lang="pt-BR">
{header(L, 'inicio')}
{''.join(views)}
{footer(L)}
</div>
<script>
{js}
</script>
'''
    (out / "index.html").write_text(page)
    return page


def main():
    articles = parse_articles()
    assert len(articles) == 4, articles.keys()
    build_dist(articles)
    page = build_preview(articles)
    print("dist/ e preview/index.html gerados;", f"{len(page) / 1024:.0f} KB na prévia")


if __name__ == "__main__":
    main()
