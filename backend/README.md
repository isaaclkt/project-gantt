# Project Grantt - Backend

Backend API para o sistema de gerenciamento de projetos com gráfico de Gantt.

## Tecnologias

- **Python 3.10+**
- **Flask 3.0** - Framework web
- **SQLAlchemy** - ORM
- **MySQL** - Banco de dados
- **Flask-CORS** - Suporte a CORS
- **Flask-JWT-Extended** - Autenticação JWT (preparado)

## Estrutura do Projeto

```
backend/
├── app/
│   ├── config/         # Configurações
│   │   ├── database.py # Conexão com banco
│   │   └── settings.py # Variáveis de ambiente
│   ├── models/         # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── team_member.py
│   ├── routes/         # Rotas da API
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   ├── team.py
│   │   └── users.py
│   ├── services/       # Lógica de negócio
│   │   ├── project_service.py
│   │   ├── task_service.py
│   │   ├── team_service.py
│   │   └── user_service.py
│   └── utils/          # Utilitários
│       ├── response.py
│       └── validators.py
├── migrations/         # Scripts SQL
│   └── schema.sql
├── requirements.txt
├── run.py              # Ponto de entrada (dev)
└── wsgi.py             # Ponto de entrada (prod)
```

## Instalação

### 1. Criar ambiente virtual

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar banco de dados MySQL

```sql
CREATE DATABASE project_grantt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Ou execute o script completo:
```bash
mysql -u root -p < migrations/schema.sql
```

### 4. Configurar variáveis de ambiente

Copie o arquivo de exemplo e edite:
```bash
cp .env.example .env
```

Edite o `.env`:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/project_grantt
JWT_SECRET_KEY=sua-chave-jwt
CORS_ORIGINS=http://localhost:3000
```

### 5. Inicializar banco de dados

```bash
# Criar tabelas
flask init-db

# Popular com dados de exemplo
flask seed-db
```

### 6. Executar servidor

```bash
python run.py
```

O servidor estará disponível em `http://localhost:5000`.

## Comandos CLI

| Comando | Descrição |
|---------|-----------|
| `flask init-db` | Criar tabelas no banco |
| `flask seed-db` | Popular banco com dados de exemplo |
| `flask reset-db` | Resetar banco (apaga todos os dados) |

## Endpoints da API

### Projetos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/projects` | Listar projetos |
| GET | `/api/projects/:id` | Obter projeto |
| POST | `/api/projects` | Criar projeto |
| PUT | `/api/projects/:id` | Atualizar projeto |
| DELETE | `/api/projects/:id` | Deletar projeto |
| GET | `/api/projects/:id/tasks` | Tarefas do projeto |

### Tarefas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/tasks` | Listar tarefas |
| GET | `/api/tasks/:id` | Obter tarefa |
| POST | `/api/tasks` | Criar tarefa |
| PATCH | `/api/tasks/:id` | Atualizar tarefa |
| DELETE | `/api/tasks/:id` | Deletar tarefa |
| PATCH | `/api/tasks/:id/status` | Atualizar status |
| PATCH | `/api/tasks/:id/progress` | Atualizar progresso |

### Equipe
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/team` | Listar membros |
| GET | `/api/team/:id` | Obter membro |
| POST | `/api/team` | Criar membro |
| PUT | `/api/team/:id` | Atualizar membro |
| DELETE | `/api/team/:id` | Deletar membro |
| GET | `/api/team/departments` | Listar departamentos |

### Usuários
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/users` | Listar usuários |
| POST | `/api/users` | Criar usuário |
| GET | `/api/user/profile` | Perfil do usuário |
| PUT | `/api/user/profile` | Atualizar perfil |
| GET | `/api/user/settings` | Configurações |
| PUT | `/api/user/settings` | Atualizar config |

### Autenticação (Preparado)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | Registro |
| POST | `/api/auth/refresh` | Atualizar token |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Usuário atual |

## Formato de Resposta

Todas as respostas seguem o padrão:

```json
{
  "data": { ... },
  "success": true,
  "message": "Operação realizada com sucesso"
}
```

Respostas paginadas:
```json
{
  "data": [ ... ],
  "success": true,
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10
  }
}
```

## Desenvolvimento

### Executar em modo debug
```bash
FLASK_ENV=development python run.py
```

### Testes
```bash
pytest
```

## Produção

Use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Documentação Completa

- [API Documentation](./API_DOCUMENTATION.md) - Documentação completa dos endpoints
- [Frontend Integration](./FRONTEND_INTEGRATION.md) - Guia de integração com o frontend

## Usuários de Teste

Após executar `flask seed-db`:

| Email | Senha | Cargo |
|-------|-------|-------|
| ana.silva@empresa.com | password123 | Project Manager |
| carlos.santos@empresa.com | password123 | Frontend Developer |
| marina.costa@empresa.com | password123 | Backend Developer |
| pedro.oliveira@empresa.com | password123 | UI/UX Designer |
| julia.ferreira@empresa.com | password123 | QA Engineer |
| rafael.mendes@empresa.com | password123 | DevOps Engineer |
