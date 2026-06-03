#!/usr/bin/env python3
"""
Gera docs/entrega-final/GymControl_ProjetoFinal.docx a partir do
documento da entrega parcial, adicionando os capítulos 9 e 10 que
descrevem a implementação realizada e o acesso ao software, e
renumerando o antigo "9 CONSIDERAÇÕES FINAIS" para "11".

Uso:
    python scripts/build-entrega-final-docx.py

Pré-requisito:
    pip install python-docx

Depois de gerar, ABRA O DOCX NO WORD e atualize os campos automáticos
(Sumário, Lista de Quadros, Lista de Figuras): clique com botão direito
em cada campo > Atualizar campo > Atualizar a tabela inteira (F9).
"""
import os
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Instale a dependência: pip install python-docx", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "docs" / "entrega-parcial" / "GymControl_Planejamento.docx"
DST  = ROOT / "docs" / "entrega-final" / "GymControl_ProjetoFinal.docx"

# ─────────────────────────────────────────────────────────────────────────────
# Conteúdo a inserir.  Cada item é (estilo, texto). Estilos disponíveis no
# documento parcial: 'Heading 1', 'Heading 2', 'Heading 3', 'Normal'.
# ─────────────────────────────────────────────────────────────────────────────

NEW_CHAPTERS = [
    ("Heading 1", "9 IMPLEMENTAÇÃO REALIZADA"),

    ("Normal",
     "Este capítulo descreve a implementação concreta do sistema GymControl, "
     "do código-fonte ao deploy. Todo o conteúdo dos capítulos 1 a 8 — descritivo "
     "computacional, requisitos, modelagem UML, tecnologias previstas, "
     "cronograma e orçamento — foi cumprido. Onde a implementação foi além "
     "do planejado, isso é registrado nas seções a seguir."),

    ("Heading 2", "9.1 Visão geral"),
    ("Normal",
     "O sistema foi entregue como uma aplicação web cliente-servidor. O "
     "front-end é uma SPA (single-page application) leve em HTML, CSS "
     "(Tailwind via CDN) e JavaScript modular. O back-end é uma API REST "
     "em Node.js com Express, persistindo dados em MySQL 8. O código está "
     "publicado no GitHub e o front-end já está no ar na Vercel."),

    ("Heading 2", "9.2 Arquitetura"),
    ("Normal",
     "O repositório segue uma estrutura clara que separa responsabilidades: "
     "o diretório lib/ concentra módulos puros (validação de CPF, "
     "autenticação JWT, sanitização de logs, migração inicial); server.js "
     "é o ponto de entrada Express com todas as rotas /api/*; public/ "
     "contém o front-end estático com index.html, styles.css e onze "
     "módulos JavaScript em public/js/ (core, dashboard, alunos, "
     "professores, planos, pagamentos, inadimplentes, frequencia, backup, "
     "professor, aluno); sql/ traz o schema, o seed e consultas de "
     "referência; tests/ guarda os testes automatizados; docs/ contém a "
     "documentação completa; infra/terraform/ define a infraestrutura como "
     "código para AWS."),

    ("Heading 2", "9.3 Backend"),
    ("Normal",
     "O back-end usa Node.js 20 com módulos ES (ESM, type=module no "
     "package.json). As dependências de produção são: express para o "
     "roteamento HTTP; mysql2/promise como driver MySQL com connection "
     "pool; bcrypt para hashing de senhas; jsonwebtoken para emissão e "
     "verificação de JWT; cookie-parser para leitura do cookie de sessão; "
     "cors com allowlist via variável de ambiente; helmet para definir "
     "headers de segurança; express-rate-limit para limitar tentativas de "
     "login e chamadas à API. Todas as queries usam binds parametrizados, "
     "eliminando a possibilidade de SQL injection."),

    ("Heading 2", "9.4 Frontend"),
    ("Normal",
     "O front-end é estático (sem build step) e funciona em qualquer "
     "servidor que sirva arquivos. A estilização usa Tailwind CSS via CDN. "
     "O JavaScript foi modularizado em onze arquivos por domínio, "
     "carregados em ordem por index.html. Todo o tratamento de eventos é "
     "feito por delegação centralizada (atributo data-action), sem nenhum "
     "handler inline no HTML. Essa decisão foi necessária para suportar "
     "uma Content Security Policy estrita, descrita na seção 9.6."),

    ("Heading 2", "9.5 Banco de dados"),
    ("Normal",
     "O banco escolhido foi MySQL 8, conforme planejado no QUADRO 11. "
     "O schema completo está em sql/01_schema.sql e implementa as oito "
     "classes do QUADRO 8 como oito tabelas (usuarios, alunos, "
     "professores, planos, pagamentos, treinos, exercicios, frequencias). "
     "Todas as chaves estrangeiras estão definidas com ações ON DELETE "
     "apropriadas (CASCADE para dependências, SET NULL para vínculos "
     "opcionais, RESTRICT onde a integridade exige). ENUMs do MySQL "
     "restringem campos categóricos (status, método de pagamento, nível "
     "de treino, tipo de usuário). Toda chave estrangeira possui índice. "
     "Dados de demonstração estão em sql/02_seed.sql. Em ambiente de "
     "desenvolvimento o banco sobe via docker-compose.yml com auto-carga "
     "do schema e do seed na primeira inicialização do volume."),

    ("Heading 2", "9.6 Endurecimento de segurança (RNF02 e RNF07)"),
    ("Normal",
     "Os requisitos não funcionais de controle de acesso (RNF02) e "
     "proteção de informações (RNF07) foram atendidos com múltiplas "
     "camadas de defesa: senhas armazenadas como hash bcrypt (custo 10); "
     "autenticação via JWT em cookie httpOnly com prefixo __Secure-, "
     "SameSite=Strict e secure=true; middleware de RBAC aplicado rota a "
     "rota conforme o QUADRO 3 (Admin, Professor, Aluno); helmet "
     "configurando Content Security Policy estrita (default-src 'self', "
     "sem 'unsafe-inline' em script-src), HSTS, X-Frame-Options DENY, "
     "X-Content-Type-Options nosniff; express-rate-limit com 120 "
     "requisições por minuto na API e 5 por minuto no endpoint de login; "
     "validação de CPF com cálculo de dígito verificador; sanitizador de "
     "logs que remove CPF, e-mail, hash bcrypt e tokens antes de qualquer "
     "console.error; log de auditoria de tentativas de login (sucesso e "
     "falha) com e-mail mascarado; redirecionamento HTTPS em produção; "
     "JWT_SECRET obrigatório em produção (a aplicação recusa subir com o "
     "valor padrão de desenvolvimento)."),

    ("Heading 2", "9.7 Testes automatizados"),
    ("Normal",
     "O sistema possui três camadas de testes automatizados que rodam na "
     "integração contínua e localmente. A camada SQL (sql/04_tests.sql) "
     "verifica que o schema rejeita inserções inválidas (UNIQUE em CPF e "
     "CREF, ENUMs, FKs órfãs, CHECK em valor negativo, CASCADE de "
     "exercícios). A camada Jest soma 106 testes em seis suítes: "
     "validators, log-sanitizer e auth são testados unitariamente sem "
     "banco; api.test.js e api.extra.test.js usam Supertest para exercitar "
     "todos os endpoints contra um MySQL real, validando a matriz RBAC do "
     "QUADRO 3; migrate.test.js cobre o parser SQL do bootstrap. A camada "
     "Playwright tem 16 testes em sete arquivos de spec, dirigindo um "
     "Chromium real para validar o fluxo completo de login, CRUD de "
     "alunos com máscara de CPF, criação de treino com exercícios pelo "
     "professor, registro de pagamento, registro de check-in, RBAC visual "
     "(o aluno não vê o menu de inadimplentes) e logout. Há também um "
     "modo \"human-paced\" que roda a suíte com pausa de um segundo entre "
     "cada ação e grava vídeo, gerando um arquivo MP4 único para revisão "
     "humana. A cobertura de linhas do back-end é de 91%, com lib/ a 100%."),

    ("Heading 2", "9.8 Containerização"),
    ("Normal",
     "A aplicação foi empacotada em uma imagem Docker multi-stage. O "
     "primeiro estágio instala apenas as dependências de produção (com "
     "compilação nativa do bcrypt). O segundo estágio copia node_modules "
     "e o código sob um usuário não-root, define HEALTHCHECK apontando "
     "para /healthz e usa tini como PID 1 para roteamento correto de "
     "sinais. O ambiente de desenvolvimento usa docker-compose.yml com "
     "MySQL 8.4 já configurado para UTF-8 e auto-carga do schema."),

    ("Heading 2", "9.9 Integração contínua e entrega contínua (CI/CD)"),
    ("Normal",
     "Há três workflows do GitHub Actions: o CI (.github/workflows/ci.yml) "
     "roda em todo push e pull request executando, nesta ordem, npm audit, "
     "lint, testes SQL, testes Jest, testes Playwright e Trivy (scanner de "
     "vulnerabilidades de container). Falha em qualquer etapa bloqueia o "
     "merge. O CodeQL (.github/workflows/codeql.yml) roda análise estática "
     "de segurança semanalmente e em pull requests, usando o conjunto de "
     "regras security-and-quality. O CD (.github/workflows/cd.yml) está "
     "implementado mas dormente: só dispara se a variável ENABLE_CD do "
     "repositório for true e o segredo AWS_DEPLOY_ROLE_ARN estiver "
     "configurado. Ele assume um role da AWS via OIDC (sem credenciais "
     "estáticas), constrói a imagem, faz scan Trivy de novo, faz push para "
     "ECR e dispara um deploy no App Runner."),

    ("Heading 2", "9.10 Deploy"),
    ("Normal",
     "O front-end está hospedado na Vercel em "
     "https://gym-control-pearl.vercel.app — deploy automático a cada push "
     "para main. A infraestrutura AWS necessária para o back-end está "
     "totalmente escrita como código em infra/terraform/: VPC com duas "
     "sub-redes privadas em zonas distintas (sem IGW, sem NAT, sem custo "
     "extra de tráfego); RDS MySQL 8 t4g.micro (free-tier por 12 meses), "
     "criptografado, em sub-rede privada; ECR para a imagem; App Runner "
     "com VPC connector para falar com o RDS, capacidade fixada em uma "
     "única instância com concorrência máxima de 25 requisições "
     "(controle de custo); Secrets Manager guardando a senha do banco e o "
     "JWT_SECRET (ambos gerados aleatoriamente pelo Terraform); CloudWatch "
     "Logs com retenção de 7 dias; AWS Budgets opcional com alertas por "
     "e-mail. O deploy real não foi efetivado para esta entrega (custo "
     "estimado de $20 USD nos dois meses do projeto), mas todo o "
     "ferramental está pronto: bastaria executar terraform apply seguido "
     "do script scripts/aws-deploy.sh."),

    # ─── Capítulo 10 ────────────────────────────────────────────────────────
    ("Heading 1", "10 ACESSO E EXECUÇÃO DO SOFTWARE"),

    ("Heading 2", "10.1 Frontend no ar"),
    ("Normal",
     "O front-end pode ser acessado em "
     "https://gym-control-pearl.vercel.app. Como o back-end não foi "
     "efetivamente publicado, as chamadas /api/* retornam erro de rede; "
     "o front-end ainda assim demonstra o layout, a tela de login e as "
     "telas dos três perfis quando inspecionado no navegador."),

    ("Heading 2", "10.2 Repositório de código"),
    ("Normal",
     "O código-fonte completo está em "
     "https://github.com/DyeAllPies/GymControl. O fork foi feito a partir "
     "do repositório original do grupo "
     "(https://github.com/eduardo2580/GymControl) e as contribuições foram "
     "enviadas de volta via pull request "
     "(https://github.com/eduardo2580/GymControl/pull/1) para registro."),

    ("Heading 2", "10.3 Execução local com Docker"),
    ("Normal",
     "Para executar o sistema localmente bastam quatro comandos a partir "
     "do diretório do repositório: \"git clone https://github.com/"
     "DyeAllPies/GymControl.git && cd GymControl\", \"npm install\", "
     "\"docker compose up -d\" (sobe o MySQL com schema e seed "
     "automaticamente) e \"npm start\" (sobe a aplicação em "
     "http://localhost:3000). As contas de demonstração estão no README. "
     "O passo a passo completo, incluindo execução sem Docker, está em "
     "docs/tutorials/ no repositório."),

    ("Heading 2", "10.4 Documentação adicional"),
    ("Normal",
     "Além deste relatório, o repositório traz documentação granular em "
     "docs/. A pasta docs/entrega-parcial/ guarda este documento na sua "
     "versão original (planejamento). A pasta docs/entrega-final/ contém "
     "documentação viva: cada um dos dez requisitos funcionais e cada um "
     "dos sete requisitos não funcionais tem um arquivo Markdown próprio "
     "com referência ao código que o implementa; há também arquivos para "
     "cada caso de uso (QUADROS 4, 5 e 6), cada classe do modelo "
     "(QUADRO 8), a relação atualizada de tecnologias e descrições das "
     "funcionalidades adicionadas além do planejamento original "
     "(autenticação, endurecimento de segurança, testes, CI/CD, "
     "containerização, backup/restore, preparação do deploy AWS). O guia "
     "operacional de deploy está em "
     "docs/entrega-final/aws-deploy-guide.md."),
]


# ─────────────────────────────────────────────────────────────────────────────
def build():
    if not SRC.exists():
        sys.exit(f"Não encontrei {SRC}")
    DST.parent.mkdir(parents=True, exist_ok=True)

    doc = Document(str(SRC))

    # Cover page mantém "Planejamento do Sistema" — o sistema ainda não está
    # em produção real (sem deploy de back-end ativo).

    # 1b. Parágrafo de organização do trabalho no capítulo 1: reescrever para
    # refletir os 11 capítulos da entrega final (era 9).
    new_intro = (
        "O trabalho está organizado em onze capítulos. Após esta introdução, "
        "o capítulo 2 apresenta o descritivo computacional do software. "
        "O capítulo 3 caracteriza o sistema. "
        "O capítulo 4 lista os requisitos funcionais e não funcionais. "
        "O capítulo 5 apresenta os diagramas UML que modelam o sistema. "
        "O capítulo 6 descreve as tecnologias escolhidas. "
        "O capítulo 7 traz o cronograma de desenvolvimento. "
        "O capítulo 8 apresenta o orçamento estimado. "
        "O capítulo 9 detalha a implementação efetivamente realizada. "
        "O capítulo 10 informa como acessar e executar o software. "
        "Por fim, o capítulo 11 traz as considerações finais. "
        "As referências utilizadas estão arroladas ao final do trabalho."
    )
    for p in doc.paragraphs:
        if "nove capítulos" in p.text:
            # Mantém o primeiro run e zera os demais, depois substitui o texto
            if p.runs:
                p.runs[0].text = new_intro
                for r in p.runs[1:]:
                    r.text = ""
            break

    # 2. Achar "9 CONSIDERAÇÕES FINAIS"
    target = None
    for p in doc.paragraphs:
        if "CONSIDERAÇÕES FINAIS" in p.text and p.text.strip().startswith("9"):
            target = p
            break
    if target is None:
        sys.exit("Não encontrei o parágrafo '9 CONSIDERAÇÕES FINAIS' no template.")

    # 3. Inserir novos capítulos ANTES dele
    for style, text in NEW_CHAPTERS:
        new_p = target.insert_paragraph_before(text, style=style)
        # justifica os normais como o resto do documento
        if style == "Normal":
            new_p.paragraph_format.first_line_indent = None  # já é normal

    # 4. Renumerar "9 CONSIDERAÇÕES FINAIS" para "11"
    if target.text.strip().startswith("9"):
        for run in target.runs:
            if "9 CONSIDERAÇÕES FINAIS" in run.text:
                run.text = run.text.replace("9 CONSIDERAÇÕES FINAIS",
                                            "11 CONSIDERAÇÕES FINAIS")
                break
        # caso o texto esteja partido em vários runs, tenta substituição no primeiro
        if target.text.strip().startswith("9"):
            # força via primeiro run
            if target.runs:
                target.runs[0].text = "11" + target.runs[0].text[1:]

    doc.save(str(DST))

    # 5. Marca todos os campos para atualizar quando o Word abrir — sumário,
    # lista de quadros, lista de figuras, referências REF. Isso evita o
    # passo manual de F9 antes de entregar.
    _force_update_fields(str(DST))

    size_kb = os.path.getsize(DST) // 1024
    print(f"OK: {DST.relative_to(ROOT)}  ({size_kb} KB)")
    print()
    print("Ao abrir o docx no Word, ele vai perguntar se deve atualizar os campos:")
    print("aceite (\"Sim\") para o Sumário, Lista de Quadros e Lista de Figuras")
    print("ficarem corretos. Não precisa rodar F9 manualmente.")


def _force_update_fields(path):
    """Liga w:updateFields no settings.xml interno do docx. Quando o Word
    abrir o arquivo, ele atualiza automaticamente o Sumário e demais campos."""
    import zipfile
    import shutil
    from xml.etree import ElementTree as ET

    NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", NS)
    tmp = path + ".tmp"

    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/settings.xml":
                root = ET.fromstring(data)
                upd = root.find(f"{{{NS}}}updateFields")
                if upd is None:
                    upd = ET.SubElement(root, f"{{{NS}}}updateFields")
                upd.set(f"{{{NS}}}val", "true")
                data = ET.tostring(root, xml_declaration=True, encoding="UTF-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)


if __name__ == "__main__":
    build()
