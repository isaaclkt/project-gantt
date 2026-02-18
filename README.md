# ProjectFlow - Sistema de Gerenciamento de Projetos

Sistema completo de gerenciamento de projetos com visualizacao Gantt interativo, controle de tarefas, equipes, compartilhamento publico e hierarquia de departamentos.

![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-16-black.svg)
![MySQL](https://img.shields.io/badge/mysql-8.0-blue.svg)

---

## Tecnologias

### Backend
- **Python 3.12** + **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **MySQL 8.0** - Banco de dados relacional
- **Flask-JWT-Extended** - Autenticacao JWT
- **Werkzeug** - Hash seguro de senhas
- **Flask-CORS** - Cross-Origin Resource Sharing

### Frontend
- **Next.js 16** - Framework React com App Router
- **TypeScript** - Tipagem estatica
- **Tailwind CSS** - Estilizacao utilitaria
- **Radix UI** - Componentes acessiveis
- **shadcn/ui** - Biblioteca de componentes
- **SWR** - Cache e revalidacao de dados
- **Lucide Icons** - Icones

---

## Funcionalidades

### 1. Autenticacao e Autorizacao (RBAC)

Sistema completo de controle de acesso baseado em roles:

| Role | Nivel | Descricao | Permissoes |
|------|-------|-----------|------------|
| `admin` | 4 | Administrador Global | Acesso total ao sistema |
| `department_admin` | 3 | Admin de Departamento | Gerencia apenas seu departamento |
| `manager` | 2 | Gerente | Gerencia projetos e equipes |
| `member` | 1 | Membro | Trabalha em tarefas atribuidas |
| `viewer` | 0 | Visualizador | Apenas visualizacao |

**Recursos:**
- Login com email/senha
- Tokens JWT com expiracao
- Alteracao de senha
- Sessoes seguras

### 2. Dashboard

- Grafico Gantt interativo com visualizacao de tarefas
- Painel de Insights Inteligentes com alertas automaticos
- Estatisticas de projetos e tarefas em tempo real
- Criacao rapida de tarefas
- Visao geral de projetos ativos

### 3. Gerenciamento de Projetos

- CRUD completo de projetos
- Status: `planning`, `active`, `on-hold`, `completed`
- Atribuicao de membros da equipe
- Cores personalizadas para identificacao visual
- Progresso automatico calculado pelas tarefas
- Datas de inicio e termino

### 4. Gerenciamento de Tarefas

- CRUD completo de tarefas
- Status: `todo`, `in-progress`, `review`, `completed`
- Prioridades: `low`, `medium`, `high`
- Atribuicao de responsavel
- Progresso de 0-100%
- Visualizacao no Gantt

### 5. Gerenciamento de Equipe

- Cadastro de membros com senha definida pelo administrador
- Minimo 8 caracteres para senha
- Atribuicao de departamentos
- Controle de status: `active`, `away`, `offline`
- Vinculacao automatica com usuario do sistema

### 6. Links de Compartilhamento

Permite compartilhar projetos publicamente sem necessidade de login:

- Geracao de links temporarios seguros
- Tokens de 32 bytes (secrets.token_urlsafe)
- Expiracao configuravel (1-30 dias)
- Visualizacao publica do Gantt
- Botao de copiar link
- **Tracking de acessos** - registra ultimo acesso e contador
- **Revogacao** - desativa link sem deletar registro

### 7. Sistema de Convites

Permite convidar novos membros para a equipe via email:

- Tokens seguros de 32 bytes
- Expiracao configuravel (1-30 dias)
- **Opcao de pre-definir senha** - admin define senha no convite
- Aceite de convite cria User + Settings + TeamMember
- Roles permitidos: manager, member, viewer (nao department_admin)
- **Scoping de departamento** - department admin só convida para seu dept
- **Revogacao** - convites invalidados por soft delete
- **Auditoria** - todos os convites sao rastreados

### 8. Hierarquia de Departamentos

- Cada departamento pode ter 1 administrador
- Admin de departamento gerencia APENAS seu departamento
- Restricao automatica de visualizacao e edicao
- Endpoints para atribuir/remover admin de departamento
- **Scoping em rotas por ID** - /projects/:id e /tasks/:id verificam departamento

### 9. Auditoria de Ações

Sistema completo de logging de eventos críticos:

- Registra todas as ações: LOGIN, LOGOUT, CREATED, UPDATED, DELETED, REVOKED
- Tracking de recursos: users, projects, tasks, invites, share_links
- **Convites**: INVITE_CREATED, INVITE_ACCEPTED, INVITE_REVOKED
- **Share Links**: SHARE.CREATED, SHARE.REVOKED
- Endereço IP e User Agent registrados
- Logs por usuário, por recurso ou recentes
- Cleanup configuravel de logs antigos

### 10. Insights Inteligentes

- Alertas de tarefas atrasadas
- Projetos com risco de atraso
- Membros sobrecarregados
- Tarefas sem responsavel
- Resumo de produtividade

### 9. Configuracoes do Usuario

- Tema: `light`, `dark`, `system`
- Idioma: Portugues BR
- Preferencias de notificacao
- Preferencias de exibicao
- Atualizacao de perfil e avatar

---

## Estrutura do Projeto

```
project-grantt/
├── backend/
│   ├── app/
│   │   ├── config/           # Configuracoes (database, app)
│   │   ├── models/           # Modelos SQLAlchemy
│   │   │   ├── user.py       # User, UserSettings
│   │   │   ├── project.py    # Project
│   │   │   ├── task.py       # Task
│   │   │   ├── team_member.py
│   │   │   ├── department.py # Department, Role
│   │   │   └── share_link.py # ShareLink
│   │   ├── routes/           # Rotas da API
│   │   │   ├── auth.py       # Autenticacao
│   │   │   ├── projects.py   # Projetos
│   │   │   ├── tasks.py      # Tarefas
│   │   │   ├── team.py       # Equipe
│   │   │   ├── admin.py      # Administracao
│   │   │   ├── share.py      # Compartilhamento
│   │   │   ├── settings.py   # Configuracoes
│   │   │   └── insights.py   # Insights
│   │   ├── services/         # Logica de negocio
│   │   └── utils/            # Utilitarios
│   │       ├── rbac.py       # Role-Based Access Control
│   │       ├── response.py   # Respostas padronizadas
│   │       └── validators.py # Validadores
│   ├── migrations/           # Scripts SQL
│   │   └── schema.sql        # Schema completo
│   ├── scripts/
│   │   └── seed_database.py  # Popular dados de teste
│   ├── .env                  # Variaveis de ambiente
│   └── run.py                # Ponto de entrada
│
└── frontend/
    ├── app/                  # Paginas Next.js (App Router)
    │   ├── page.tsx          # Dashboard
    │   ├── login/            # Pagina de login
    │   ├── projects/         # Pagina de projetos
    │   ├── tasks/            # Pagina de tarefas
    │   ├── team/             # Pagina da equipe
    │   ├── settings/         # Configuracoes
    │   └── shared/[token]/   # Visualizacao publica
    ├── components/           # Componentes React
    │   ├── ui/               # Componentes base (shadcn/ui)
    │   ├── layout/           # DashboardLayout, Header, Sidebar
    │   ├── gantt/            # Grafico Gantt
    │   ├── dashboard/        # Componentes do dashboard
    │   ├── projects/         # ProjectCard, ProjectFormDialog, ShareDialog
    │   ├── tasks/            # TaskCard, TaskFormDialog
    │   └── team/             # TeamMemberCard, TeamMemberFormDialog
    ├── contexts/             # Contextos React
    │   └── auth-context.tsx  # Contexto de autenticacao
    └── lib/                  # Utilitarios e services
        ├── services/         # Chamadas API
        │   ├── auth-service.ts
        │   ├── project-service.ts
        │   ├── task-service.ts
        │   ├── team-service.ts
        │   ├── share-service.ts
        │   └── settings-service.ts
        ├── types.ts          # Tipos TypeScript
        ├── permissions.ts    # Helpers de permissao
        └── utils.ts          # Utilitarios gerais
```

---

## Banco de Dados

### Tabelas

| Tabela | Descricao |
|--------|-----------|
| `departments` | Departamentos da organizacao |
| `roles` | Cargos/funcoes (job titles) |
| `users` | Usuarios do sistema |
| `user_settings` | Configuracoes do usuario |
| `team_members` | Membros da equipe |
| `projects` | Projetos |
| `project_members` | Relacao N:M projeto-membro |
| `tasks` | Tarefas |
| `share_links` | Links de compartilhamento |
| `audit_logs` | Logs de auditoria de acoes |
| `invites` | Convites para novos membros |

### Diagrama de Relacionamentos

```
departments 1---1 users (admin_id)
departments 1---* users (department_id)
departments 1---* invites

users 1---1 user_settings
users 1---1 team_members
users 1---* projects (owner_id)
users 1---* share_links (created_by)
users 1---* invites (created_by)
users 1---* audit_logs

projects *---* team_members (via project_members)
projects 1---* tasks
projects 1---* share_links

team_members 1---* tasks (assignee_id)
```

### Views

- `v_tasks_detailed` - Tarefas com informacoes de projeto e responsavel
- `v_projects_summary` - Projetos com contagem de membros e tarefas

### Triggers

- `after_task_update` - Atualiza progresso do projeto
- `after_task_insert` - Atualiza progresso do projeto
- `after_task_delete` - Atualiza progresso do projeto

---

## API Endpoints

### Autenticacao
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| POST | `/api/auth/login` | - | Login |
| POST | `/api/auth/logout` | JWT | Logout |
| GET | `/api/auth/me` | JWT | Usuario atual |
| PUT | `/api/auth/change-password` | JWT | Alterar senha |

### Projetos
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/projects` | JWT | Listar projetos |
| POST | `/api/projects` | Manager+ | Criar projeto |
| GET | `/api/projects/:id` | JWT | Obter projeto |
| PUT | `/api/projects/:id` | Manager+ | Atualizar projeto |
| DELETE | `/api/projects/:id` | Admin | Excluir projeto |

### Tarefas
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/tasks` | JWT | Listar tarefas |
| POST | `/api/tasks` | Member+ | Criar tarefa |
| GET | `/api/tasks/:id` | JWT | Obter tarefa |
| PUT | `/api/tasks/:id` | Member+ | Atualizar tarefa |
| DELETE | `/api/tasks/:id` | Manager+ | Excluir tarefa |

### Equipe
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/team` | JWT | Listar membros |
| POST | `/api/team` | Manager+ | Criar membro (requer senha) |
| GET | `/api/team/:id` | JWT | Obter membro |
| PUT | `/api/team/:id` | Manager+ | Atualizar membro |
| DELETE | `/api/team/:id` | Manager+ | Excluir membro |

### Compartilhamento
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| POST | `/api/share/projects/:id` | Manager+ | Criar link |
| GET | `/api/share/projects/:id/links` | Manager+ | Listar links |
| DELETE | `/api/share/links/:id` | Criador/Admin | Revogar link (soft delete) |
| GET | `/api/share/public/:token` | **Publico** | Visualizar Gantt (com tracking) |

### Convites
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| POST | `/api/invites` | Manager+ | Criar convite |
| GET | `/api/invites` | Manager+ | Listar convites (com scoping) |
| GET | `/api/invites/:id` | Manager+ | Obter convite |
| DELETE | `/api/invites/:id` | Criador/Admin | Revogar convite |
| POST | `/api/invites/:token/accept` | **Publico** | Aceitar convite e criar usuario |
| GET | `/api/invites/validate/:token` | **Publico** | Validar convite |

### Auditoria
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/audit/logs` | Admin | Listar logs de auditoria |

### Administracao
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/admin/departments` | JWT | Listar departamentos |
| POST | `/api/admin/departments` | Admin | Criar departamento |
| PUT | `/api/admin/departments/:id` | Admin | Atualizar departamento |
| DELETE | `/api/admin/departments/:id` | Admin | Excluir departamento |
| PUT | `/api/admin/departments/:id/admin` | Admin | Atribuir admin |
| DELETE | `/api/admin/departments/:id/admin` | Admin | Remover admin |

### Configuracoes
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/settings` | JWT | Obter configuracoes |
| PUT | `/api/settings` | JWT | Atualizar configuracoes |
| GET | `/api/profile` | JWT | Obter perfil |
| PUT | `/api/profile` | JWT | Atualizar perfil |

### Insights
| Metodo | Endpoint | Auth | Descricao |
|--------|----------|------|-----------|
| GET | `/api/insights` | JWT | Obter insights |

---

## Instalacao

### Pre-requisitos
- Python 3.12+
- Node.js 18+
- MySQL 8.0+

### 1. Configurar Banco de Dados

```bash
# Criar banco de dados
mysql -u root -p

CREATE DATABASE project_grantt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# Executar schema
cd backend
mysql -u root -p project_grantt < migrations/schema.sql
```

### 2. Configurar Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
# Editar .env com suas credenciais MySQL

# Popular dados de teste
python scripts/seed_database.py

# Iniciar servidor
python run.py
```

Backend disponivel em: `http://localhost:5000`

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Criar arquivo de ambiente
echo "NEXT_PUBLIC_API_URL=http://localhost:5000/api" > .env.local

# Iniciar servidor
npm run dev
```

Frontend disponivel em: `http://localhost:3000`

---

## Contas de Teste

| Cargo | Email | Senha |
|-------|-------|-------|
| Admin | admin@projectflow.com | admin123 |
| Gerente | gerente@projectflow.com | gerente123 |
| Membro | membro@projectflow.com | membro123 |
| Viewer | viewer@projectflow.com | viewer123 |

---

## Formato de Respostas da API

### Sucesso
```json
{
  "success": true,
  "data": { ... },
  "message": "Operacao realizada com sucesso"
}
```

### Erro
```json
{
  "success": false,
  "data": null,
  "message": "Descricao do erro"
}
```

### Paginacao
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 100,
    "totalPages": 2
  }
}
```

---

## Variaveis de Ambiente

### Backend (.env)
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua_secret_key_aqui
DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/project_grantt
JWT_SECRET_KEY=sua_jwt_secret_aqui
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
PORT=5000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

---

## Seguranca

- Autenticacao JWT com tokens seguros
- Senhas hasheadas com Werkzeug (pbkdf2:sha256)
- RBAC (Role-Based Access Control)
- Validacao de inputs
- CORS configurado
- Soft delete para dados sensiveis
- Tokens de compartilhamento seguros (32 bytes)

---

## Autor

Desenvolvido por **Isaac** com auxilio do Claude AI.

---

Se tiver duvidas ou sugestoes, abra uma issue no repositorio.
