# Project Gantt

Sistema completo de gerenciamento de projetos com gráfico Gantt interativo, desenvolvido com Flask (Backend) e Next.js (Frontend).

![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

## Funcionalidades

### Dashboard
- Gráfico Gantt interativo com visualização de tarefas
- Painel de Insights Inteligentes com alertas automáticos
- Estatísticas de projetos e tarefas em tempo real
- Criação rápida de tarefas

### Gerenciamento de Projetos
- CRUD completo de projetos
- Atribuição de membros da equipe
- Acompanhamento de progresso
- Status: Planejamento, Em Andamento, Concluído, Cancelado

### Gerenciamento de Tarefas
- CRUD completo de tarefas
- Prioridades: Baixa, Média, Alta, Crítica
- Status: Pendente, Em Progresso, Concluída, Cancelada
- Atribuição a membros da equipe
- Datas de início e término

### Equipe
- Cadastro de membros da equipe
- Departamentos e cargos
- Vinculação com usuários do sistema
- Visualização de carga de trabalho

### Insights Inteligentes
- Alertas de tarefas atrasadas
- Projetos com risco de atraso
- Membros sobrecarregados
- Tarefas sem responsável
- Resumo de produtividade

### Configurações
- Tema claro/escuro
- Idioma (Português BR)
- Configurações de notificações
- Atualização de perfil e senha

## Tecnologias

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **JWT** - Autenticação com tokens
- **SQLite** - Banco de dados (configurável)

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes UI
- **Recharts** - Gráficos

## Instalação

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- npm ou yarn

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Executar
python run.py
```

O backend estará disponível em `http://localhost:5000`

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

## Estrutura do Projeto

```
project-gantt/
├── backend/
│   ├── app/
│   │   ├── config/         # Configurações do banco e app
│   │   ├── models/         # Modelos do SQLAlchemy
│   │   ├── routes/         # Endpoints da API
│   │   ├── services/       # Lógica de negócio
│   │   └── utils/          # Utilitários (auth, validators)
│   ├── tests/              # Testes automatizados
│   ├── uploads/            # Arquivos enviados
│   └── requirements.txt
│
├── frontend/
│   ├── app/                # Páginas (App Router)
│   ├── components/         # Componentes React
│   │   ├── dashboard/      # Componentes do dashboard
│   │   ├── gantt/          # Gráfico Gantt
│   │   ├── layout/         # Header, Sidebar
│   │   ├── projects/       # Componentes de projetos
│   │   ├── settings/       # Componentes de configurações
│   │   ├── tasks/          # Componentes de tarefas
│   │   ├── team/           # Componentes de equipe
│   │   └── ui/             # Componentes base (shadcn)
│   ├── contexts/           # Contextos React
│   ├── lib/
│   │   └── services/       # Serviços de API
│   └── public/             # Arquivos estáticos
│
└── README.md
```

## API Endpoints

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register` | Registrar usuário |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| POST | `/api/auth/refresh` | Renovar token |

### Projetos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/projects` | Listar projetos |
| POST | `/api/projects` | Criar projeto |
| GET | `/api/projects/:id` | Obter projeto |
| PUT | `/api/projects/:id` | Atualizar projeto |
| DELETE | `/api/projects/:id` | Excluir projeto |

### Tarefas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/tasks` | Listar tarefas |
| POST | `/api/tasks` | Criar tarefa |
| GET | `/api/tasks/:id` | Obter tarefa |
| PUT | `/api/tasks/:id` | Atualizar tarefa |
| DELETE | `/api/tasks/:id` | Excluir tarefa |

### Equipe
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/team` | Listar membros |
| POST | `/api/team` | Criar membro |
| PUT | `/api/team/:id` | Atualizar membro |
| DELETE | `/api/team/:id` | Excluir membro |

### Insights
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/insights` | Obter insights |

## Banco de Dados

### Tabelas Principais
- **users** - Usuários do sistema
- **user_settings** - Configurações do usuário
- **projects** - Projetos
- **tasks** - Tarefas
- **team_members** - Membros da equipe
- **project_members** - Relação projeto-membro (N:M)
- **departments** - Departamentos
- **roles** - Cargos

## Segurança

- Autenticação JWT com refresh tokens
- Blacklist de tokens para logout seguro
- RBAC (Role-Based Access Control)
- Rate limiting por IP
- Sanitização de inputs
- Validação de uploads

## Testes

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Autor

Desenvolvido por **Isaac** com auxílio do Claude AI.

---

Se tiver dúvidas ou sugestões, abra uma issue no repositório.
