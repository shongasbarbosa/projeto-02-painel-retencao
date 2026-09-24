# Painel de Retenção

[![CI](https://github.com/shongasbarbosa/projeto-02-painel-retencao/actions/workflows/ci.yml/badge.svg)](https://github.com/shongasbarbosa/projeto-02-painel-retencao/actions/workflows/ci.yml)
[![Deploy](https://github.com/shongasbarbosa/projeto-02-painel-retencao/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/shongasbarbosa/projeto-02-painel-retencao/actions/workflows/deploy-pages.yml)
[![Demo no GitHub Pages](https://img.shields.io/badge/demo-GitHub%20Pages-2563eb)](https://shongasbarbosa.github.io/projeto-02-painel-retencao/)

Painel para equipes de tutoria/suporte de uma plataforma de EaD identificarem
alunos em risco de evasão, priorizarem quem contatar e registrarem o
resultado dos contatos, comparando turmas. Projeto 2 de um portfólio de 5
projetos voltado a uma bolsa de Desenvolvedor Web em um projeto de EaD
baseado em Moodle.

**Demo online (dados fictícios, sem backend):**
https://shongasbarbosa.github.io/projeto-02-painel-retencao/

## Problema

A equipe de tutoria precisa saber, entre centenas de alunos, quais estão
prestes a desistir, para agir antes que isso aconteça. Sem um painel
centralizado, essa priorização depende de olhar planilhas ou relatórios
soltos do Moodle, o que é lento e inconsistente entre turmas.

## Funcionalidades

- **Dashboard** com KPIs (matriculados, ativos, em risco, desistentes,
  concluintes, taxa de evasão), funil de retenção e distribuição por faixa
  de risco.
- **Lista priorizada de contato**: filtros por curso e faixa de risco,
  busca por aluno, registro de contato (sem resposta / retornou /
  desistiu) em diálogo, histórico de contatos por aluno e exportação CSV.
- **Comparação entre turmas**: gráficos lado a lado de taxa de evasão e de
  alunos ativos vs. em risco.
- **Modo demonstração**: toda a aplicação funciona sem backend, com dados
  fictícios gerados pelo mesmo script de seed do backend.
- **Tema claro/escuro/sistema**, persistente, acessível (WCAG AA) e sem
  flash ao carregar.

## Stack

| Camada | Tecnologias |
| --- | --- |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16, Pydantic v2, JWT, ruff |
| Frontend | Vue 3 + TypeScript (strict), Vite, Quasar, Pinia, Vue Router, ECharts |
| Infra | Docker, Docker Compose, Nginx, GitHub Actions |

## Decisões técnicas do backend

- **Gerenciamento de dependências**: `pip` + `pyproject.toml` (PEP 621),
  em vez de `uv`. O projeto é pequeno o suficiente para não sentir a
  diferença de velocidade do `uv`, e `pip`/`pyproject.toml` continuam
  sendo o caminho mais universal (sem exigir uma ferramenta adicional
  instalada) para quem for rodar o projeto localmente sem Docker.
- **Hashing de senha**: `bcrypt` diretamente, em vez de `passlib[bcrypt]`.
  O `passlib` está sem manutenção ativa e tem um bug conhecido de
  incompatibilidade com versões recentes do `bcrypt` (>= 4.1); usar o
  `bcrypt` diretamente evita esse problema.
- **JWT**: [`PyJWT`](https://pyjwt.readthedocs.io/), seguindo a recomendação
  atual da própria documentação do FastAPI, em vez de `python-jose`. O
  `python-jose` está com manutenção mais lenta; `PyJWT` é a biblioteca
  citada nos exemplos oficiais de autenticação JWT do FastAPI.

## Arquitetura

```mermaid
flowchart LR
    subgraph Cliente
        B[Navegador]
    end

    subgraph "Modo API real (Docker)"
        B -->|HTTP| N[Nginx / frontend]
        N -->|"/api/*"| API[FastAPI]
        API --> PG[(PostgreSQL 16)]
    end

    subgraph "Modo demonstração (GitHub Pages)"
        B -->|dados estáticos| J[demo-data/seed.json]
        J --> C[Cálculo de score no cliente]
    end
```

## Modelo de dados

```mermaid
erDiagram
    STUDENTS ||--o{ ENROLLMENTS : possui
    COURSES ||--o{ ENROLLMENTS : recebe
    COURSES ||--o{ ACTIVITIES : define
    ENROLLMENTS ||--o{ SUBMISSIONS : gera
    ACTIVITIES ||--o{ SUBMISSIONS : recebe
    STUDENTS ||--o{ CONTACT_LOGS : recebe

    STUDENTS {
        int id PK
        string name
        string email
        string phone
    }
    COURSES {
        int id PK
        string name
        string category
    }
    ENROLLMENTS {
        int id PK
        int student_id FK
        int course_id FK
        enum status
        datetime enrolled_at
        datetime last_access_at
        datetime completed_at
    }
    ACTIVITIES {
        int id PK
        int course_id FK
        string title
        int weight
    }
    SUBMISSIONS {
        int id PK
        int enrollment_id FK
        int activity_id FK
        datetime submitted_at
    }
    CONTACT_LOGS {
        int id PK
        int student_id FK
        int course_id FK
        datetime contacted_at
        enum outcome
        text notes
    }
    USERS {
        int id PK
        string name
        string email
        string hashed_password
    }
```

## Regra de score de risco

```
score = 0.6 * min(dias_inativo / 30, 1) + 0.4 * (1 - % atividades entregues)
```

Faixas: **baixo** (score < 0,4), **médio** (0,4 a 0,7), **alto** (> 0,7).

A regra é uma função pura ([`app/services/risk_score.py`](backend/app/services/risk_score.py)
no backend e [`src/services/riskScore.ts`](frontend/src/services/riskScore.ts)
no frontend, para o modo demonstração), testada isoladamente nos dois
lados. A mesma fórmula será reaproveitada no plugin Moodle do projeto 5
deste portfólio.

**Exemplos:**

| Dias inativo | % entregue | Cálculo | Score | Faixa |
| --- | --- | --- | --- | --- |
| 0 | 100% | 0,6·0 + 0,4·0 | 0,00 | baixo |
| 15 | 50% | 0,6·0,5 + 0,4·0,5 | 0,50 | médio |
| 45 | 0% | 0,6·1 + 0,4·1 | 1,00 | alto |

## Endpoints da API

Documentação interativa completa em `/docs` (Swagger) e `/redoc` (ReDoc).

| Método | Rota | Descrição |
| --- | --- | --- |
| POST | `/api/auth/login` | Autentica e retorna token JWT |
| GET | `/api/courses` | Lista cursos |
| POST | `/api/enrollments` | Cria matrícula |
| PATCH | `/api/enrollments/{id}/status` | Atualiza status da matrícula |
| GET | `/api/reports/funnel?course_id=` | Funil de retenção |
| GET | `/api/reports/risk-score?course_id=&level=` | Lista de risco ordenada |
| POST | `/api/students/{id}/contact-logs` | Registra contato |
| GET | `/api/students/{id}/contact-logs` | Histórico de contatos |
| GET | `/api/reports/comparison?course_ids=1,2` | Compara turmas |
| GET | `/api/reports/risk-score/export?course_id=` | Exporta CSV |
| GET | `/health` | Health check |

**Exemplo — login:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@painelretencao.com", "password": "demo123456"}'
```

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

**Exemplo — lista de risco:**

```bash
curl "http://localhost:8000/api/reports/risk-score?level=alto" \
  -H "Authorization: Bearer eyJhbGciOi..."
```

```json
[
  {
    "enrollment_id": 42,
    "student_id": 17,
    "student_name": "Aluno 17",
    "course_id": 1,
    "course_name": "Introdução à Programação",
    "days_inactive": 38,
    "submission_rate": 0.1,
    "score": 0.92,
    "level": "alto"
  }
]
```

## Qualidade e testes

**Backend.** A suíte roda com `pytest` contra um PostgreSQL 16 real (não
SQLite), para que o comportamento de enums, timestamps com timezone e
constraints seja o mesmo do ambiente de produção. Ela cobre:

- a regra de score de risco (limites das faixas, saturação da
  inatividade em 30 dias);
- autenticação e permissões (login inválido, endpoints protegidos sem
  token ou com token inválido);
- os relatórios de funil, score de risco e comparação entre turmas;
- o fluxo de matrícula e de registro/consulta de contatos.

`ruff check` e `ruff format --check` rodam junto, garantindo lint e
formatação consistentes.

**Migration.** A migration `0001` é conferida contra os modelos com
`alembic revision --autogenerate`: se o schema criado pela migration
divergir dos modelos SQLAlchemy, esse comando gera uma revisão não-vazia
apontando a diferença. Uma migration vazia confirma que os dois batem.

**Seed.** O script (`backend/scripts/seed.py`) não cria tabelas — ele
exige que a migration já tenha rodado, e falha com uma mensagem clara
orientando `alembic upgrade head` caso contrário. É idempotente: rodar
duas vezes seguidas não duplica alunos, matrículas nem atividades, e a
cada execução reexporta `frontend/src/demo-data/seed.json` com o estado
atual do banco (não apenas os registros criados naquela execução), para
que o modo demonstração do frontend sempre reflita os dados reais.

**Ponta a ponta com Docker.** Um único `docker compose up --build` aplica
a migration e roda o seed automaticamente antes de subir a API (ver
`backend/docker-entrypoint.sh`). Esse fluxo é testado do zero (`docker
compose down -v` seguido de `docker compose up --build`), cobrindo
health check, login, dashboard, lista de contato com registro de
contato, comparação entre turmas e exportação CSV, tanto via `/docs`
quanto via o frontend.

**Frontend.** `eslint`, `vue-tsc` e `vitest` cobrem a regra de score
replicada no cliente e a camada de serviço do modo demonstração (login,
funil, ordenação por risco, registro de contato em memória). O build de
produção e o build em modo demonstração (com `--base` apontando para o
GitHub Pages) são verificados, assim como as telas via
`npm run screenshots` (Playwright), com os prints revisados manualmente
em `docs/screenshots`.

## CI/CD

A cada push ou pull request para `main`, o workflow de CI
(`.github/workflows/ci.yml`) roda dois jobs em paralelo:

- **backend**: sobe um PostgreSQL como service container, instala as
  dependências, roda `ruff check`, `ruff format --check` e `pytest`;
- **frontend**: instala as dependências, roda `eslint`, `vue-tsc`,
  `vitest` e o build de produção.

O deploy (`.github/workflows/deploy-pages.yml`) builda o frontend em modo
demonstração com o `base` do GitHub Pages e publica em
`shongasbarbosa.github.io/projeto-02-painel-retencao`.

## Como rodar com Docker

Pré-requisitos: Docker e Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:8080
- API (Swagger): http://localhost:8000/docs

O container da API roda as migrations e o seed automaticamente na
inicialização (idempotente — pode subir o compose várias vezes sem
duplicar dados). Login demo: `demo@painelretencao.com` / `demo123456`.

## Como rodar os testes

**Backend** (requer um PostgreSQL de teste real — não SQLite):

```bash
# sobe só o banco (a partir da raiz do projeto) e cria o banco de teste
docker compose up -d db
docker compose exec db psql -U postgres -c "CREATE DATABASE painel_retencao_test;"

cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows; source .venv/bin/activate no Linux/macOS
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

Por padrão os testes se conectam em
`postgresql+psycopg://postgres:postgres@localhost:5432/painel_retencao_test`;
ajuste a variável de ambiente `TEST_DATABASE_URL` se a sua porta for
diferente (por exemplo, se já existir outro PostgreSQL rodando localmente
na 5432 — nesse caso, defina `POSTGRES_PORT=5433` no seu `.env` e aponte
`TEST_DATABASE_URL`/`DATABASE_URL` para a mesma porta).

**Frontend:**

```bash
cd frontend
npm ci
npm run lint
npx vue-tsc -b
npm run test
```

## Modo demonstração vs. API real

| | Modo demonstração | API real |
| --- | --- | --- |
| Backend necessário | Não | Sim (Docker) |
| Dados | Fixos, gerados pelo seed, em `frontend/src/demo-data/seed.json` | Vivos, no PostgreSQL |
| Cálculo de score | No cliente (mesma fórmula) | No servidor |
| Registro de contato | Em memória (perdido ao recarregar) | Persistido no banco |
| Como ativar | `VITE_DEMO_MODE=true` | `VITE_DEMO_MODE=false` + `VITE_API_URL` |

O deploy no GitHub Pages roda sempre em modo demonstração, pois a Pages
serve apenas arquivos estáticos.

## Deploy da API

Este repositório não publica a API automaticamente — apenas o frontend
(modo demonstração) vai para o GitHub Pages. Para publicar a API de fato,
qualquer serviço com plano gratuito que suporte containers Docker e
PostgreSQL gerenciado serve, por exemplo:

1. Criar um serviço PostgreSQL gerenciado (o próprio provedor costuma
   oferecer um plano gratuito com um banco pequeno).
2. Publicar a imagem de `backend/Dockerfile` apontando `DATABASE_URL` para
   esse banco.
3. Definir as variáveis de ambiente de `.env.example` (principalmente
   `JWT_SECRET`, `DEMO_USER_EMAIL/PASSWORD`).
4. Apontar `VITE_API_URL` do frontend para a URL pública da API e refazer
   o build (ou publicar um segundo frontend, fora do modo demonstração).

Nenhum deploy da API foi feito neste momento — esta seção é apenas um guia
de como fazê-lo quando for necessário.

## Screenshots

| Login | Dashboard (desktop) |
| --- | --- |
| ![Login](docs/screenshots/01-login.png) | ![Dashboard desktop](docs/screenshots/02-dashboard-desktop-claro.png) |

| Dashboard (mobile) | Lista de contato |
| --- | --- |
| ![Dashboard mobile](docs/screenshots/03-dashboard-mobile.png) | ![Lista de contato](docs/screenshots/04-contato-dialogo.png) |

| Comparação entre turmas | Tema escuro |
| --- | --- |
| ![Comparação](docs/screenshots/05-comparacao.png) | ![Dashboard escuro](docs/screenshots/06-dashboard-escuro.png) |

## Git

Histórico organizado em commits pequenos, no padrão
[Conventional Commits](https://www.conventionalcommits.org/), agrupados
por etapa (setup, modelos, regra de score, endpoints, seed, testes,
frontend, tema, docker, CI, docs). Nenhum commit contém linha de
coautoria.

## Competências demonstradas

- Relatórios da plataforma (funil, comparação entre turmas, exportação).
- Aferição de taxas de abandono/desistência/evasão (regra de score
  documentada e testada).
- Serviços de suporte ao usuário (lista priorizada de contato, histórico).
- Desenvolvimento de API com FastAPI e Python, com documentação de
  endpoints (Swagger/ReDoc).
- Frontend com Vue.js/Quasar e TypeScript.
- Banco de dados PostgreSQL modelado com SQLAlchemy/Alembic.
- Containerização com Docker e Docker Compose.
- Controle de versão com Git (commits organizados, CI/CD com GitHub
  Actions).

## Autor

**Dhyego Barbosa** — [github.com/shongasbarbosa](https://github.com/shongasbarbosa)
