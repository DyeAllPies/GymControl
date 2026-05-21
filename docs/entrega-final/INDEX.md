# Documentação — GymControl

Fonte: [GymControl_Planejamento.docx](GymControl_Planejamento.docx) (entregue na disciplina **EV 50775 — Prática Profissional**).

## Status

- ✅ Implementado
- 🟡 Parcial
- 🔴 Pendente

## Requisitos funcionais (QUADRO 1)

| Código | Requisito | Status |
|---|---|---|
| [RF01](requirements/rf/RF01.md) | Cadastro de alunos | ✅ |
| [RF02](requirements/rf/RF02.md) | Edição e exclusão de alunos | ✅ |
| [RF03](requirements/rf/RF03.md) | Cadastro de professores | ✅ |
| [RF04](requirements/rf/RF04.md) | Cadastro de planos | ✅ |
| [RF05](requirements/rf/RF05.md) | Registrar pagamentos | ✅ |
| [RF06](requirements/rf/RF06.md) | Consultar inadimplentes | ✅ |
| [RF07](requirements/rf/RF07.md) | Cadastro de treinos | ✅ |
| [RF08](requirements/rf/RF08.md) | Vincular treinos a alunos | ✅ |
| [RF09](requirements/rf/RF09.md) | Registrar frequência | ✅ |
| [RF10](requirements/rf/RF10.md) | Relatórios | ✅ |

## Requisitos não funcionais (QUADRO 2)

| Código | Requisito | Status |
|---|---|---|
| [RNF01](requirements/rnf/RNF01.md) | Interface simples e intuitiva | ✅ |
| [RNF02](requirements/rnf/RNF02.md) | Controle de acesso por tipo de usuário | ✅ |
| [RNF03](requirements/rnf/RNF03.md) | Banco relacional | ✅ |
| [RNF04](requirements/rnf/RNF04.md) | Acessível por navegador | ✅ |
| [RNF05](requirements/rnf/RNF05.md) | Boa organização visual | ✅ |
| [RNF06](requirements/rnf/RNF06.md) | Consultas rápidas | ✅ |
| [RNF07](requirements/rnf/RNF07.md) | Proteger informações dos usuários | ✅ |

## Modelagem

- **Casos de uso** (QUADROS 4, 5, 6): [cadastrar-aluno](requirements/casos-de-uso/cadastrar-aluno.md) · [registrar-pagamento](requirements/casos-de-uso/registrar-pagamento.md) · [cadastrar-treino](requirements/casos-de-uso/cadastrar-treino.md)
- **Classes do modelo** (QUADRO 8): [Usuario](requirements/classes/usuario.md) · [Aluno](requirements/classes/aluno.md) · [Professor](requirements/classes/professor.md) · [Plano](requirements/classes/plano.md) · [Pagamento](requirements/classes/pagamento.md) · [Treino](requirements/classes/treino.md) · [Exercicio](requirements/classes/exercicio.md) · [Frequencia](requirements/classes/frequencia.md)
- **Tecnologias** (QUADRO 11): [tecnologias.md](requirements/tecnologias.md)

## Operação

- **[Guia de deploy na AWS](aws-deploy-guide.md)** — passo a passo para subir o backend e conectar com o frontend já no ar na Vercel.

## Adicionado durante o desenvolvimento (fora do docx)

Itens que não estavam no planejamento original mas foram incorporados (alguns reforçando RNF02 e RNF07):

- [Autenticação JWT + bcrypt](added/autenticacao.md)
- [Endurecimento de segurança (helmet, rate-limit, validação)](added/seguranca.md)
- [Suíte de testes automatizados (Jest + Playwright)](added/testes-automatizados.md)
- [CI/CD (GitHub Actions, Vercel)](added/ci-cd.md)
- [Ambiente de desenvolvimento com Docker](added/docker-dev.md)
- [Backup e restore via API](added/backup-restore.md)
