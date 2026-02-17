# ProjectFlow - Documentacao Completa do Projeto

## Sumario

1. [Visao Geral](#1-visao-geral)
2. [Stack Tecnologica](#2-stack-tecnologica)
3. [Arquitetura do Sistema](#3-arquitetura-do-sistema)
4. [Backend (Flask)](#4-backend-flask)
5. [Frontend (Next.js)](#5-frontend-nextjs)
6. [Banco de Dados](#6-banco-de-dados)
7. [Autenticacao e Seguranca](#7-autenticacao-e-seguranca)
8. [Sistema de Permissoes (RBAC)](#8-sistema-de-permissoes-rbac)
9. [Funcionalidades por Modulo](#9-funcionalidades-por-modulo)
10. [API - Endpoints Completos](#10-api---endpoints-completos)
11. [Estrutura de Arquivos](#11-estrutura-de-arquivos)
12. [Como Executar](#12-como-executar)
13. [Testes](#13-testes)
14. [Decisoes Tecnicas](#14-decisoes-tecnicas)

---

## 1. Visao Geral

**ProjectFlow** e uma plataforma completa de gestao de projetos com visualizacao Gantt interativa. Permite que equipes planejem, executem e acompanhem projetos com controle de tarefas, membros, permissoes e preferencias de usuario.

### O que o sistema faz

- Gerenciamento completo de projetos (CRUD) com status e progresso
- Gerenciamento de tarefas com atribuicao, prioridade e acompanhamento
- Gestao de equipe com departamentos, cargos e status de disponibilidade
- Grafico Gantt interativo com visualizacao por dia, semana e mes
- Autenticacao JWT com refresh token automatico
- Controle de acesso baseado em papeis (RBAC) com 4 niveis
- Painel administrativo para departamentos e cargos
- Sistema de preferencias funcionais (tema, modo compacto, avatares)
- Upload de avatar de usuario
- Busca global com Ctrl+K
- Interface totalmente em PT-BR
- Tema claro, escuro e automatico (sistema)
- Landing page publica para visitantes

---

## 2. Stack Tecnologica

### Backend

| Tecnologia | Versao | Finalidade |
|------------|--------|------------|
| Python | 3.9+ | Linguagem principal |
| Flask | 3.0.0 | Framework web |
| SQLAlchemy | 2.0.23 | ORM (mapeamento objeto-relacional) |
| Flask-Migrate | 4.0.5 | Migracoes de banco de dados |
| Flask-JWT-Extended | 4.6.0 | Autenticacao JWT |
| Flask-CORS | 4.0.0 | Cross-Origin Resource Sharing |
| Flask-Limiter | 3.5.0 | Rate limiting |
| PyMySQL | 1.1.0 | Driver MySQL |
| Redis | 5.0.1 | Blacklist de tokens e cache |
| Bleach | 6.1.0 | Sanitizacao de HTML |
| Pytest | 7.4.3 | Testes automatizados |

### Frontend

| Tecnologia | Versao | Finalidade |
|------------|--------|------------|
| Next.js | 16.1.6 | Framework React com App Router |
| React | 18.3.1 | Biblioteca de interface |
| TypeScript | 5.x | Tipagem estatica |
| Tailwind CSS | 4.1.9 | Estilizacao utility-first |
| Radix UI | 1.x/2.x | Componentes acessiveis (base do shadcn/ui) |
| SWR | 2.3.8 | Data fetching e cache |
| React Hook Form | 7.60.0 | Gerenciamento de formularios |
| Zod | 3.25.76 | Validacao de schemas |
| Recharts | 2.15.4 | Graficos (Gantt chart) |
| Lucide React | 0.454.0 | Icones |
| next-themes | 0.4.6 | Gerenciamento de tema |
| Jest | 30.2.0 | Testes automatizados |

### Banco de Dados

| Tecnologia | Finalidade |
|------------|------------|
| MySQL 5.7+ | Banco relacional principal |
| Redis (opcional) | Cache e blacklist de tokens |

---

## 3. Arquitetura do Sistema

```
┌─────────────────┐         ┌─────────────────┐
│                 │  HTTP   │                 │
│   Frontend      │ ◄─────► │   Backend       │
│   Next.js       │  :3000  │   Flask         │
│   (React + TS)  │         │   (Python)      │
│                 │         │                 │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ SWR Cache                 │ SQLAlchemy ORM
         │                           │
         │                  ┌────────▼────────┐
         │                  │                 │
         │                  │   MySQL         │
         │                  │   Database      │
         │                  │                 │
         │                  └────────┬────────┘
         │                           │
         │                  ┌────────▼────────┐
         │                  │   Redis         │
         │                  │   (Token Cache) │
         │                  └─────────────────┘
```

### Fluxo de dados

1. Usuario interage com o **frontend** (Next.js)
2. Frontend faz requisicoes HTTP para a **API** (Flask) na porta 5000
3. Backend valida o **JWT token** no header Authorization
4. Backend verifica **permissoes RBAC** do usuario
5. **Service layer** executa a logica de negocio
6. **ORM (SQLAlchemy)** traduz para queries SQL
7. **MySQL** persiste os dados
8. Resposta retorna em formato JSON padronizado
9. Frontend atualiza a UI via **SWR** (revalidacao automatica)

---

## 4. Backend (Flask)

### Estrutura de pastas

```
backend/
├── app/
│   ├── __init__.py              # Fabrica da aplicacao Flask
│   ├── config/
│   │   ├── database.py          # Configuracao SQLAlchemy
│   │   └── settings.py          # Variaveis de configuracao
│   ├── models/
│   │   ├── user.py              # User + UserSettings
│   │   ├── project.py           # Project
│   │   ├── task.py              # Task
│   │   ├── team_member.py       # TeamMember + project_members
│   │   └── department.py        # Department + Role
│   ├── routes/
│   │   ├── auth.py              # /api/auth/*
│   │   ├── users.py             # /api/users/* + /api/user/*
│   │   ├── projects.py          # /api/projects/*
│   │   ├── tasks.py             # /api/tasks/*
│   │   ├── team.py              # /api/team/*
│   │   └── admin.py             # /api/admin/*
│   ├── services/
│   │   ├── user_service.py      # Logica de usuarios
│   │   ├── project_service.py   # Logica de projetos
│   │   ├── task_service.py      # Logica de tarefas
│   │   ├── team_service.py      # Logica de equipe
│   │   └── admin_service.py     # Logica administrativa
│   └── utils/
│       ├── response.py          # Formatacao de respostas
│       ├── rbac.py              # Decoradores de permissao
│       ├── validators.py        # Validacao de entrada
│       ├── rate_limiter.py      # Rate limiting
│       ├── sanitizer.py         # Sanitizacao de inputs
│       └── token_blacklist.py   # Blacklist de JWT
├── tests/                       # Suite de testes (69 testes)
├── uploads/avatars/             # Avatares enviados
├── .env                         # Variaveis de ambiente
├── requirements.txt             # Dependencias Python
├── run.py                       # Ponto de entrada
└── wsgi.py                      # Entrada para producao (Gunicorn)
```

### Camadas da aplicacao

**Routes (Rotas)** — Recebem a requisicao HTTP, extraem parametros, chamam o service e retornam a resposta JSON. Nao contem logica de negocio.

**Services (Servicos)** — Contem toda a logica de negocio: validacoes, regras, calculos. Interagem com os models via SQLAlchemy.

**Models (Modelos)** — Representam as tabelas do banco. Definem campos, relacionamentos e metodos de serializacao (`to_dict()`).

**Utils (Utilitarios)** — Funcoes transversais: formatacao de resposta, RBAC, validacao, sanitizacao, rate limiting.

### Formato de resposta padrao

Toda resposta da API segue o mesmo formato:

```json
// Sucesso
{
  "success": true,
  "data": { ... },
  "message": "Operacao realizada com sucesso"
}

// Sucesso paginado
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 47,
    "totalPages": 5
  }
}

// Erro
{
  "success": false,
  "data": null,
  "message": "Descricao do erro"
}
```

---

## 5. Frontend (Next.js)

### Estrutura de pastas

```
frontend/
├── app/                         # Paginas (App Router)
│   ├── layout.tsx               # Layout raiz (providers)
│   ├── page.tsx                 # Dashboard / Landing page
│   ├── globals.css              # Estilos globais + tema
│   ├── login/page.tsx           # Pagina de login
│   ├── register/page.tsx        # Pagina de cadastro
│   ├── projects/page.tsx        # Gestao de projetos
│   ├── team/page.tsx            # Gestao de equipe
│   ├── settings/page.tsx        # Configuracoes do usuario
│   ├── admin/page.tsx           # Painel administrativo
│   ├── error.tsx                # Pagina de erro
│   └── not-found.tsx            # Pagina 404
├── components/
│   ├── landing/                 # Landing page publica
│   ├── layout/                  # DashboardLayout, Header, Sidebar
│   ├── gantt/                   # GanttChart, GanttTaskBar, GanttTooltip
│   ├── dashboard/               # StatsCards
│   ├── projects/                # ProjectCard, ProjectFormDialog, ProjectDetailDialog
│   ├── tasks/                   # TaskFormDialog, TaskDetailDialog
│   ├── team/                    # TeamMemberCard, TeamMemberFormDialog
│   ├── settings/                # ProfileSection, PreferencesSection, etc.
│   ├── auth/                    # ProtectedRoute
│   ├── ui/                      # 50+ componentes shadcn/ui
│   └── theme-provider.tsx       # Provider de tema
├── contexts/
│   ├── auth-context.tsx         # Estado de autenticacao
│   └── settings-context.tsx     # Estado de preferencias
├── lib/
│   ├── types.ts                 # Interfaces TypeScript
│   ├── api-config.ts            # Configuracao da API + error handling
│   ├── permissions.ts           # Checagem de permissoes (client-side)
│   ├── gantt-utils.ts           # Calculos do Gantt chart
│   ├── utils.ts                 # Funcoes utilitarias
│   └── services/                # Camada de servicos (API calls)
│       ├── task-service.ts
│       ├── project-service.ts
│       ├── team-service.ts
│       ├── settings-service.ts
│       └── admin-service.ts
└── hooks/
    └── use-mobile.ts            # Hook de responsividade
```

### Paginas e rotas

| Rota | Autenticacao | Descricao |
|------|-------------|-----------|
| `/` | Nao → Landing page / Sim → Dashboard | Pagina principal |
| `/login` | Nao | Formulario de login |
| `/register` | Nao | Formulario de cadastro |
| `/projects` | Sim | Lista e gestao de projetos |
| `/team` | Sim | Lista e gestao de equipe |
| `/settings` | Sim | Perfil, senha, preferencias, notificacoes |
| `/admin` | Sim (Admin) | Departamentos e cargos |

### Context Providers

A aplicacao usa 3 providers aninhados no `layout.tsx`:

```
ThemeProvider          → Controla tema (claro/escuro/sistema)
  └── AuthProvider     → Controla autenticacao (user, login, logout)
       └── SettingsProvider  → Controla preferencias (compacto, avatares, etc.)
```

**AuthContext** (`contexts/auth-context.tsx`):
- Armazena: `user`, `isAuthenticated`, `isLoading`
- Metodos: `login()`, `logout()`, `refreshUser()`
- Persiste tokens no `localStorage`
- Verifica autenticacao no mount da aplicacao

**SettingsContext** (`contexts/settings-context.tsx`):
- Armazena: `settings` (tema, idioma, preferencias de exibicao)
- Usa SWR para fetch automatico de `/user/settings`
- Metodos: `updateSettings()`, `mutateSettings()`
- Consumido por: DashboardLayout (modo compacto), Header (avatares), team page (avatares)

### Gerenciamento de estado

| Tipo | Tecnologia | Uso |
|------|-----------|-----|
| Estado global de auth | React Context | User, tokens, login/logout |
| Estado global de settings | React Context + SWR | Preferencias, tema |
| Estado de dados (listas) | SWR | Projetos, tarefas, equipe, perfil |
| Estado local de UI | useState | Dialogs, formularios, filtros |
| Tema | next-themes | Claro/escuro/sistema |

### API Client (`lib/api-config.ts`)

Funcao central `apiFetch()` que:
- Adiciona `Authorization: Bearer <token>` automaticamente
- Detecta `FormData` e remove `Content-Type` (para upload)
- Intercepta erro 401 e tenta **refresh token** automatico
- Classifica erros com codigos padrao (`ERROR_CODES`)
- Faz retry transparente apos renovar o token

---

## 6. Banco de Dados

### Diagrama de tabelas

```
┌──────────────┐     ┌──────────────────┐
│   users      │     │  user_settings   │
│──────────────│     │──────────────────│
│ id (UUID)    │──1──│ user_id (FK)     │
│ name         │     │ theme            │
│ email        │     │ language         │
│ password_hash│     │ notifications    │
│ avatar       │     │ display_prefs    │
│ role         │     └──────────────────┘
│ department   │
│ status       │
└──────┬───────┘
       │
       │ 1:1 (opcional)
       ▼
┌──────────────┐     ┌──────────────────┐
│ team_members │     │  project_members │
│──────────────│     │  (associacao)    │
│ id (UUID)    │──*──│ team_member_id   │
│ user_id (FK) │     │ project_id       │
│ name         │     │ role             │
│ email        │     └────────┬─────────┘
│ role         │              │
│ department   │              │
│ status       │              *
└──────┬───────┘     ┌────────▼─────────┐
       │             │   projects       │
       │             │──────────────────│
       │             │ id (UUID)        │
       │ assignee    │ name             │
       │             │ status           │
       *             │ progress         │
┌──────▼───────┐     │ start_date       │
│   tasks      │     │ end_date         │
│──────────────│     │ owner_id (FK)    │
│ id (UUID)    │──*──│                  │
│ name         │     └──────────────────┘
│ status       │
│ priority     │     ┌──────────────────┐
│ progress     │     │  departments     │
│ start_date   │     │──────────────────│
│ end_date     │     │ id, name, desc   │
│ assignee_id  │     └──────────────────┘
│ project_id   │
└──────────────┘     ┌──────────────────┐
                     │  roles           │
                     │──────────────────│
                     │ id, name, desc   │
                     └──────────────────┘
```

### Tabelas detalhadas

**users** — Contas de usuario
| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | UUID | Chave primaria |
| name | VARCHAR | Nome completo |
| email | VARCHAR (unique) | E-mail de login |
| password_hash | VARCHAR | Senha criptografada (Werkzeug) |
| avatar | VARCHAR | URL do avatar |
| role | ENUM | admin, manager, member, viewer |
| department | VARCHAR | Departamento |
| phone | VARCHAR | Telefone |
| timezone | VARCHAR | Fuso horario |
| status | ENUM | active, away, offline |
| is_active | BOOLEAN | Conta ativa |
| created_at | DATETIME | Data de criacao |

**user_settings** — Preferencias do usuario
| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | UUID | Chave primaria |
| user_id | UUID (FK, unique) | Referencia ao usuario |
| theme | VARCHAR | light, dark, system |
| language | VARCHAR | pt-BR, en, es |
| notifications | JSON | Configuracoes de notificacao |
| display_preferences | JSON | compactMode, showAvatars, defaultView |

**projects** — Projetos
| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | UUID | Chave primaria |
| name | VARCHAR | Nome do projeto |
| description | TEXT | Descricao |
| color | VARCHAR | Cor hex (#3b82f6) |
| status | ENUM | planning, active, on-hold, completed |
| progress | INTEGER | 0-100 (calculado das tarefas) |
| start_date | DATE | Data de inicio |
| end_date | DATE | Data de termino |
| owner_id | UUID (FK) | Dono do projeto |

**tasks** — Tarefas
| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | UUID | Chave primaria |
| name | VARCHAR | Nome da tarefa |
| description | TEXT | Descricao |
| status | ENUM | todo, in-progress, review, completed |
| priority | ENUM | low, medium, high |
| progress | INTEGER | 0-100 |
| start_date | DATE | Data de inicio |
| end_date | DATE | Data de termino |
| assignee_id | UUID (FK) | Membro responsavel |
| project_id | UUID (FK) | Projeto associado |

**team_members** — Membros da equipe
| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | UUID | Chave primaria |
| user_id | UUID (FK, nullable) | Vinculo com conta de usuario |
| name | VARCHAR | Nome completo |
| email | VARCHAR (unique) | E-mail |
| role | VARCHAR | Cargo na empresa |
| department | VARCHAR | Departamento |
| status | ENUM | active, away, offline |
| joined_at | DATETIME | Data de ingresso |

**departments** / **roles** — Tabelas de referencia
| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | UUID | Chave primaria |
| name | VARCHAR (unique) | Nome |
| description | VARCHAR | Descricao |

---

## 7. Autenticacao e Seguranca

### Fluxo de autenticacao

```
1. Login
   POST /api/auth/login { email, password }
   → Backend valida credenciais
   → Retorna { accessToken (15min), refreshToken (30 dias) }
   → Frontend armazena no localStorage

2. Requisicao autenticada
   GET /api/projects
   Header: Authorization: Bearer <accessToken>
   → Backend decodifica JWT, identifica usuario
   → Retorna dados

3. Token expirado (automatico)
   → apiFetch recebe 401
   → Chama POST /api/auth/refresh com refreshToken
   → Recebe novo accessToken
   → Repete a requisicao original (transparente para o usuario)

4. Logout
   POST /api/auth/logout
   → Backend adiciona token a blacklist
   → Frontend limpa localStorage
   → Redireciona para /login
```

### Mecanismos de seguranca

| Mecanismo | Implementacao |
|-----------|---------------|
| Senhas | Hash com Werkzeug (pbkdf2:sha256) |
| Tokens | JWT com expiracoes curtas (15min access, 30d refresh) |
| Token blacklist | Redis ou in-memory |
| Rate limiting | Flask-Limiter (login: limitado por IP) |
| CORS | Configurado para localhost:3000 |
| Input sanitization | Bleach (remove HTML/XSS) |
| Validacao | Decoradores customizados + Zod no frontend |
| RBAC | Decoradores por rota (@require_permission) |

---

## 8. Sistema de Permissoes (RBAC)

### Matriz de permissoes

| Acao | Viewer | Member | Manager | Admin |
|------|--------|--------|---------|-------|
| Ver projetos | Sim | Sim | Sim | Sim |
| Criar projetos | - | - | Sim | Sim |
| Editar projetos | - | - | Sim | Sim |
| Excluir projetos | - | - | - | Sim |
| Ver tarefas | Sim | Sim | Sim | Sim |
| Criar tarefas | - | Sim | Sim | Sim |
| Editar tarefas | - | Sim | Sim | Sim |
| Excluir tarefas | - | - | Sim | Sim |
| Gerenciar equipe | - | - | Sim | Sim |
| Painel admin | - | - | - | Sim |

### Implementacao

**Backend** (`utils/rbac.py`):
- Decoradores: `@require_auth`, `@require_permission(perm)`, `@require_manager`
- Verificacao a nivel de rota antes de qualquer logica

**Frontend** (`lib/permissions.ts`):
- Funcoes: `canCreateProject(role)`, `canEditTask(role)`, `canManageTeam(role)`, etc.
- Usadas para esconder/mostrar botoes na UI
- Nao substitui a verificacao do backend (defesa em profundidade)

---

## 9. Funcionalidades por Modulo

### Landing Page
- Hero com titulo e CTAs
- Preview visual do dashboard (mock interativo)
- Secao de features (4 cards)
- Secao "Como funciona" (3 passos)
- CTA final + footer
- Responsiva e com suporte a tema

### Dashboard (pagina principal)
- Cards de estatisticas (total, a fazer, em progresso, concluidas)
- Grafico Gantt interativo com barras coloridas por status
- Modos de visualizacao: dia, semana, mes
- Tooltip no hover das tarefas
- Botao "Nova Tarefa" (visivel por permissao)
- Dialog de detalhes e edicao de tarefa

### Projetos
- Lista de projetos em cards com progresso visual
- Filtros por status (planejamento, ativo, pausado, concluido)
- Busca por nome
- CRUD completo com dialogs
- Atribuicao de membros ao projeto
- Calculo automatico de progresso baseado nas tarefas

### Equipe
- Grid de cards por departamento
- Filtros por status (ativo, ausente, offline) e departamento
- Busca por nome, email ou cargo
- Indicador visual de status (bolinha colorida)
- CRUD completo com dialog
- Departamentos e cargos carregados do backend

### Configuracoes
- **Perfil**: nome, email, telefone, departamento, cargo, fuso horario, avatar
- **Senha**: alteracao com validacao de senha atual
- **Preferencias**: tema (claro/escuro/sistema), modo compacto, mostrar avatares
- **Notificacoes**: toggles para email, push, lembretes, atualizacoes

### Admin
- Gerenciamento de departamentos (CRUD)
- Gerenciamento de cargos/funcoes (CRUD)
- Dialogs de confirmacao para exclusao
- Restrito a usuarios com role "admin"

### Gantt Chart
- Calculo automatico de range de datas baseado nas tarefas
- 3 modos de visualizacao (dia, semana, mes)
- Barras coloridas por status:
  - Azul = A Fazer
  - Amarelo = Em Progresso
  - Roxo = Em Revisao
  - Verde = Concluida
- Linha vermelha indicando "hoje"
- Tooltip com detalhes da tarefa no hover
- Legenda de cores
- Responsivo

---

## 10. API - Endpoints Completos

### Autenticacao (`/api/auth`)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/auth/login` | Login (retorna tokens) |
| POST | `/auth/register` | Cadastro de usuario |
| POST | `/auth/refresh` | Renovar access token |
| POST | `/auth/logout` | Invalidar token |
| GET | `/auth/me` | Dados do usuario logado |
| POST | `/auth/change-password` | Alterar senha |
| GET | `/auth/verify` | Verificar validade do token |

### Usuarios (`/api/user`, `/api/users`)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/user/profile` | Perfil do usuario logado |
| PUT | `/user/profile` | Atualizar perfil |
| GET | `/user/settings` | Configuracoes do usuario |
| PUT | `/user/settings` | Atualizar configuracoes |
| POST | `/user/avatar` | Upload de avatar |
| GET | `/uploads/avatars/:filename` | Servir avatar (publico) |
| GET | `/users` | Listar usuarios (paginado) |
| GET | `/users/:id` | Buscar usuario por ID |
| POST | `/users` | Criar usuario (admin) |

### Projetos (`/api/projects`)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/projects` | Listar projetos (filtros: status, page, limit) |
| GET | `/projects/:id` | Buscar projeto por ID |
| POST | `/projects` | Criar projeto (manager+) |
| PUT | `/projects/:id` | Atualizar projeto |
| DELETE | `/projects/:id` | Excluir projeto (admin) |
| GET | `/projects/:id/tasks` | Tarefas do projeto |
| GET | `/projects/:id/members` | Membros do projeto |
| POST | `/projects/:id/members/:memberId` | Adicionar membro |
| DELETE | `/projects/:id/members/:memberId` | Remover membro |

### Tarefas (`/api/tasks`)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/tasks` | Listar tarefas (filtros: projectId, status, assigneeId, priority) |
| GET | `/tasks/:id` | Buscar tarefa por ID |
| POST | `/tasks` | Criar tarefa (member+) |
| PUT | `/tasks/:id` | Atualizar tarefa |
| DELETE | `/tasks/:id` | Excluir tarefa (manager+) |
| PATCH | `/tasks/:id/status` | Atualizar status rapido |
| PATCH | `/tasks/:id/progress` | Atualizar progresso rapido |

### Equipe (`/api/team`)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/team` | Listar membros (filtros: department, status) |
| GET | `/team/:id` | Buscar membro por ID |
| POST | `/team` | Criar membro (manager+) |
| PUT | `/team/:id` | Atualizar membro |
| DELETE | `/team/:id` | Excluir membro (manager+) |
| PATCH | `/team/:id/status` | Atualizar status |
| GET | `/team/departments` | Listar departamentos |

### Admin (`/api/admin`)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/admin/departments` | Listar departamentos |
| POST | `/admin/departments` | Criar departamento |
| PUT | `/admin/departments/:id` | Atualizar departamento |
| DELETE | `/admin/departments/:id` | Excluir departamento |
| GET | `/admin/roles` | Listar cargos |
| POST | `/admin/roles` | Criar cargo |
| PUT | `/admin/roles/:id` | Atualizar cargo |
| DELETE | `/admin/roles/:id` | Excluir cargo |

---

## 11. Estrutura de Arquivos

### Arvore completa

```
project-grantt/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config/
│   │   │   ├── database.py
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── task.py
│   │   │   ├── team_member.py
│   │   │   └── department.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── projects.py
│   │   │   ├── tasks.py
│   │   │   ├── team.py
│   │   │   └── admin.py
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   ├── project_service.py
│   │   │   ├── task_service.py
│   │   │   ├── team_service.py
│   │   │   └── admin_service.py
│   │   └── utils/
│   │       ├── response.py
│   │       ├── rbac.py
│   │       ├── validators.py
│   │       ├── rate_limiter.py
│   │       ├── sanitizer.py
│   │       └── token_blacklist.py
│   ├── tests/
│   ├── uploads/avatars/
│   ├── .env
│   ├── requirements.txt
│   ├── run.py
│   └── wsgi.py
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── projects/page.tsx
│   │   ├── team/page.tsx
│   │   ├── settings/page.tsx
│   │   ├── admin/page.tsx
│   │   ├── error.tsx
│   │   └── not-found.tsx
│   ├── components/
│   │   ├── landing/landing-page.tsx
│   │   ├── layout/
│   │   ├── gantt/
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── tasks/
│   │   ├── team/
│   │   ├── settings/
│   │   ├── auth/
│   │   └── ui/ (50+ componentes)
│   ├── contexts/
│   │   ├── auth-context.tsx
│   │   └── settings-context.tsx
│   ├── lib/
│   │   ├── types.ts
│   │   ├── api-config.ts
│   │   ├── permissions.ts
│   │   ├── gantt-utils.ts
│   │   └── services/
│   ├── package.json
│   └── tsconfig.json
│
└── DOCUMENTACAO.md
```

---

## 12. Como Executar

### Pre-requisitos

- Python 3.9+
- Node.js 18+
- MySQL 5.7+
- Redis (opcional, para producao)

### Backend

```bash
# Entrar na pasta
cd backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
# Editar .env com suas credenciais de banco

# Criar banco de dados
flask db upgrade

# Executar servidor
python run.py
# ou
flask run --debug

# Servidor disponivel em http://localhost:5000
```

### Frontend

```bash
# Entrar na pasta
cd frontend

# Instalar dependencias
npm install

# Executar servidor de desenvolvimento
npm run dev
# ou
npx next dev

# Servidor disponivel em http://localhost:3000
```

### Variaveis de ambiente (.env)

```env
# Backend (.env)
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta
JWT_SECRET_KEY=sua-chave-jwt
DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/project_grantt
CORS_ORIGINS=http://localhost:3000
```

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

---

## 13. Testes

### Backend (69 testes - Pytest)

```bash
cd backend
pytest                     # Executar todos
pytest -v                  # Modo verboso
pytest tests/test_auth.py  # Teste especifico
```

Cobertura:
- Autenticacao (login, registro, refresh, logout)
- CRUD de projetos
- CRUD de tarefas
- CRUD de equipe
- Permissoes RBAC
- Validacoes de entrada
- Casos de erro

### Frontend (40 testes - Jest)

```bash
cd frontend
npm test                   # Executar todos
npm test -- --watch        # Modo watch
npm test -- --coverage     # Com cobertura
```

Cobertura:
- Renderizacao de componentes
- Interacao do usuario
- Chamadas de API (mocked)
- Contextos de autenticacao
- Permissoes na UI

---

## 14. Decisoes Tecnicas

### Por que Flask + Next.js?

**Flask** foi escolhido por ser leve, flexivel e permitir controle total sobre a arquitetura. A separacao em routes/services/models segue o padrao de service layer, facilitando testes e manutencao.

**Next.js** foi escolhido pelo App Router, server-side rendering e otimizacoes automaticas. O Turbopack acelera o desenvolvimento com hot reload rapido.

### Por que SWR em vez de React Query?

SWR e mais leve e se integra naturalmente com Next.js (ambos sao do Vercel). Para este projeto, a revalidacao automatica e o cache stale-while-revalidate sao suficientes.

### Por que JWT em vez de sessoes?

JWT permite que o frontend e backend sejam completamente desacoplados. O access token curto (15min) + refresh token longo (30d) equilibra seguranca e experiencia do usuario. O refresh automatico no `apiFetch` torna a renovacao transparente.

### Por que RBAC com 4 niveis?

Quatro papeis cobrem os cenarios mais comuns:
- **Admin**: controle total (TI, gerente geral)
- **Manager**: gestao de projetos e equipe (lider de equipe)
- **Member**: trabalha em tarefas (desenvolvedor, designer)
- **Viewer**: apenas visualiza (stakeholder, cliente)

### Por que shadcn/ui?

Componentes acessiveis (Radix UI) com estilizacao customizavel (Tailwind). Nao e uma biblioteca — os componentes sao copiados para o projeto, permitindo modificacao total sem dependencia externa.

### Por que SQLAlchemy em vez de raw SQL?

O ORM abstrai a complexidade do SQL, previne SQL injection por padrao, e permite trocar de banco (MySQL → PostgreSQL) sem alterar o codigo da aplicacao.

### Por que Context API em vez de Redux?

O estado global do projeto e simples: usuario autenticado e preferencias. Context API resolve isso sem a complexidade adicional do Redux. Para dados de lista (projetos, tarefas), o SWR gerencia o cache.

---

*Documento gerado para o projeto ProjectFlow — Plataforma de Gestao de Projetos com Gantt Chart*
