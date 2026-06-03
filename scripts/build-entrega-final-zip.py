#!/usr/bin/env python3
"""
Empacota o ZIP da Entrega Final com:
  - README_ENTREGA_FINAL.md (gerado aqui)
  - docs/entrega-final/GymControl_ProjetoFinal.docx
  - test-results/human-e2e.mp4
  - todo o código-fonte versionado (git ls-files)

Saída: docs/entrega-final/GymControl_EntregaFinal.zip
"""
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "docs" / "entrega-final" / "GymControl_EntregaFinal.zip"
DOCX = ROOT / "docs" / "entrega-final" / "GymControl_ProjetoFinal.docx"
VIDEO = ROOT / "test-results" / "human-e2e.mp4"

README = """# GymControl — Entrega Final
Disciplina EV 50775 — Prática Profissional: Projeto de Software
Universidade São Francisco — Análise e Desenvolvimento de Sistemas
Junho de 2026

Este ZIP é a entrega final do trabalho. Contém o relatório revisado da
entrega parcial (com os capítulos adicionais que descrevem a
implementação realizada) e o software desenvolvido na íntegra, como
exigido pelo enunciado da disciplina.

## Como esta entrega cumpre os requisitos do enunciado

O enunciado pede, para a Entrega Final:

> Documento revisado da primeira entrega com adição do software
> desenvolvido (um link para download ou um arquivo).

- O **documento revisado** está em `GymControl_ProjetoFinal.docx`. Ele
  preserva os capítulos 1–8 originais da entrega parcial (descritivo
  computacional, caracterização, requisitos, diagramas UML, tecnologias,
  cronograma, orçamento) e acrescenta:
  - **Capítulo 9 — Implementação realizada** (10 seções cobrindo visão
    geral, arquitetura, backend, frontend, banco de dados, endurecimento
    de segurança, testes automatizados, containerização, CI/CD e
    deploy, mais a seção 9.11 de rastreabilidade de requisitos).
  - **Capítulo 10 — Acesso e execução do software** (frontend no ar,
    repositório, execução local com Docker, documentação adicional).
  - **Capítulo 11 — Considerações finais** (era o capítulo 9 da
    parcial, apenas renumerado).
- O **software desenvolvido** está em `source/` (este ZIP) e também
  versionado em https://github.com/DyeAllPies/GymControl. Forkado de
  https://github.com/eduardo2580/GymControl.

Os itens listados como obrigatórios na Entrega Parcial continuam
presentes no documento, todos com a mesma numeração da parcial original:

| Item do enunciado | Onde está no docx |
| --- | --- |
| 1. Descritivo Computacional do Software | Capítulo 2 |
| 2. Tecnologia(s) escolhida(s) | Capítulo 6 (QUADRO 11) |
| 3. Cronograma de desenvolvimento | Capítulo 7 (QUADRO 12) |
| 4. Caracterização do Sistema | Capítulo 3 |
| 4.1. Nome do Sistema | Seção 3.1 |
| 4.2.1. Diagrama de Caso de Uso | Seção 5.1.1 (FIGURA 1) |
| 4.2.2. Diagrama de Sequência | Seção 5.1.3 (FIGURA 2) |
| 4.3.1. Diagrama de Classe | Seção 5.2.1 (FIGURA 3) |
| 4.3.2. Diagrama de Componentes | Seção 5.2.2 (FIGURA 4) |
| 4.4. Orçamento para desenvolvimento | Capítulo 8 (QUADRO 13) |

## O que tem neste ZIP

- `README_ENTREGA_FINAL.md` — este arquivo.
- `GymControl_ProjetoFinal.docx` — relatório revisado (documento
  principal da entrega).
- `human-e2e.mp4` — vídeo único da suíte Playwright executada em modo
  "human-paced" (pausa de 1 s entre ações), gravando o fluxo completo
  da aplicação: login admin, CRUD de alunos com máscara de CPF, criação
  de treino pelo professor, registro de pagamento, registro de check-in,
  validação visual de RBAC (aluno não vê menu de inadimplentes) e
  logout. Serve como evidência audiovisual de que o software funciona
  fim a fim.
- `source/` — todo o código-fonte versionado do projeto, exatamente
  como aparece no repositório (sem `node_modules`, sem cache do
  Terraform, sem artefatos de teste). Para rodar localmente bastam
  quatro comandos a partir de `source/`:

      npm install
      docker compose up -d
      npm start

  Documentação técnica granular (requisitos um a um, casos de uso,
  classes, segurança, CI/CD, deploy AWS, tutoriais) está em
  `source/docs/`. O README principal do projeto está em
  `source/README.md` e tem o passo a passo completo.

## Autores

Trabalho do grupo coordenado por Eduardo (eduardo2580 no GitHub).
Repositório oficial em https://github.com/eduardo2580/GymControl.
"""


def main():
    if not DOCX.exists():
        sys.exit(f"Não encontrei {DOCX}. Rode scripts/build-entrega-final-docx.py antes.")
    if not VIDEO.exists():
        sys.exit(f"Não encontrei {VIDEO}.")

    # Lista de arquivos versionados, gerada pelo git, garantindo
    # consistência com o que está no repo e excluindo node_modules,
    # .terraform, etc.
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    tracked = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    # Itens já adicionados separadamente no topo do ZIP — não duplicar
    # dentro de source/.
    skip_in_source = {
        "docs/entrega-final/GymControl_ProjetoFinal.docx",
        "test-results/human-e2e.mp4",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("README_ENTREGA_FINAL.md", README)
        z.write(DOCX, "GymControl_ProjetoFinal.docx")
        z.write(VIDEO, "human-e2e.mp4")
        for rel in tracked:
            if rel in skip_in_source:
                continue
            src = ROOT / rel
            if not src.is_file():
                continue
            z.write(src, f"source/{rel}")

    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"OK: {OUT.relative_to(ROOT)}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
