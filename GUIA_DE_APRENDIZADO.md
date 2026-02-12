# Guia de Aprendizado - ProjectFlow

## Como ler este guia

Este documento explica **cada arquivo** e **cada funcao** do projeto como se voce nunca tivesse programado. Leia na ordem — cada secao usa conceitos explicados nas anteriores.

---

# PARTE 1 — CONCEITOS BASICOS

Antes de olhar o codigo, voce precisa entender alguns conceitos.

## O que e Frontend e Backend?

Imagine um restaurante:
- **Frontend** e o salao — o que o cliente ve (mesas, cardapio, decoracao)
- **Backend** e a cozinha — onde a comida e preparada (logica, dados, regras)
- **Banco de dados** e o estoque — onde os ingredientes ficam guardados

No nosso projeto:
- **Frontend (Next.js)** = o site que o usuario ve no navegador
- **Backend (Flask)** = o servidor que processa dados e regras
- **MySQL** = o banco de dados que guarda tudo

## Como eles conversam?

O frontend faz **requisicoes HTTP** para o backend. E como pedir algo num balcao:

```
Frontend: "Me da a lista de projetos" (GET /api/projects)
Backend:  "Aqui esta" (retorna JSON com os projetos)

Frontend: "Cria esse projeto novo" (POST /api/projects, com dados)
Backend:  "Criado com sucesso" (retorna o projeto criado)
```

Os metodos HTTP sao:
- **GET** = buscar dados (ler)
- **POST** = criar algo novo
- **PUT** = atualizar algo existente (tudo)
- **PATCH** = atualizar algo existente (parcial)
- **DELETE** = excluir algo

## O que e JSON?

JSON e o formato que frontend e backend usam para trocar dados. E como um dicionario:

```json
{
  "name": "Meu Projeto",
  "status": "active",
  "progress": 45
}
```

## O que e JWT?

JWT (JSON Web Token) e um "cracha digital". Quando voce faz login, o backend te da um token. Em toda requisicao seguinte, voce mostra esse token pra provar quem voce e. Como um cracha de empresa — voce mostra na portaria e o seguranca sabe que voce pode entrar.

## O que e RBAC?

RBAC (Role-Based Access Control) = Controle de Acesso Baseado em Papeis. Cada usuario tem um papel (admin, manager, member, viewer), e cada papel pode fazer certas coisas. O admin pode tudo, o viewer so pode ver.

---

# PARTE 2 — BACKEND (A COZINHA)

O backend e feito em **Python** usando o framework **Flask**.

---

## 2.1 — Ponto de entrada: `run.py`

Este e o primeiro arquivo que roda quando voce inicia o servidor.

```python
from app import create_app    # Importa a funcao que cria o app
app = create_app()            # Cria a aplicacao Flask
app.run(debug=True, port=5000)  # Roda na porta 5000
```

**O que faz:** Cria o servidor e coloca ele pra rodar. `debug=True` faz ele reiniciar automaticamente quando voce muda o codigo. `port=5000` significa que o servidor escuta em `http://localhost:5000`.

---

## 2.2 — Fabrica da aplicacao: `app/__init__.py`

Este arquivo cria e configura toda a aplicacao Flask. Funciona como uma fabrica — monta todas as pecas.

**Funcao `create_app()`** — A funcao principal. Ela:
1. Cria a instancia do Flask
2. Carrega as configuracoes (banco de dados, JWT, etc.)
3. Configura CORS (permite que o frontend se comunique)
4. Configura JWT (autenticacao por token)
5. Configura rate limiting (limite de requisicoes)
6. Inicializa o banco de dados
7. Registra todas as rotas (auth, users, projects, tasks, team, admin)
8. Cria a pasta de uploads para avatares

**Funcao `_init_upload_dirs(app)`** — Cria a pasta `uploads/avatars/` se nao existir. E onde os avatares dos usuarios sao salvos.

**Comando CLI `seed`** — Um comando especial (`flask seed`) que popula o banco com dados de exemplo: 8 usuarios, 7 membros de equipe, 5 projetos e 10 tarefas. Util para testar.

---

## 2.3 — Configuracoes: `app/config/`

### `settings.py` — Todas as configuracoes do sistema

Este arquivo define todas as variaveis de configuracao. Pense nele como o "manual de instrucoes" do servidor.

**Classe `Config`** (configuracao base):
- `SECRET_KEY` — Chave secreta usada para criptografia. Deve ser unica e secreta.
- `SQLALCHEMY_DATABASE_URI` — Endereco do banco de dados MySQL
- `JWT_SECRET_KEY` — Chave para assinar os tokens JWT
- `JWT_ACCESS_TOKEN_EXPIRES` — Quanto tempo o token de acesso dura (15 minutos)
- `JWT_REFRESH_TOKEN_EXPIRES` — Quanto tempo o token de renovacao dura (30 dias)
- `UPLOAD_FOLDER` — Pasta onde os avatares sao salvos
- `MAX_CONTENT_LENGTH` — Tamanho maximo de upload (5MB)
- `ALLOWED_AVATAR_EXTENSIONS` — Formatos aceitos: png, jpg, jpeg, gif, webp

**Classe `DevelopmentConfig`** — Configuracoes extras para desenvolvimento (debug ativo)

**Classe `ProductionConfig`** — Configuracoes para producao (mais restritivas)

**Classe `TestingConfig`** — Configuracoes para testes (usa banco SQLite em memoria)

### `database.py` — Configuracao do banco de dados

```python
db = SQLAlchemy()    # Cria a instancia do ORM
migrate = Migrate()  # Cria a instancia de migracoes
```

**O que e ORM?** ORM (Object-Relational Mapping) permite que voce trabalhe com o banco de dados usando objetos Python em vez de escrever SQL puro. Em vez de `SELECT * FROM users WHERE id = 1`, voce escreve `User.query.get(1)`.

**`init_db(app)`** — Conecta o SQLAlchemy e o Migrate ao app Flask.

**`reset_db()`** — Apaga todas as tabelas e recria do zero. Cuidado: perde todos os dados.

---

## 2.4 — Models (Modelos): `app/models/`

Models sao classes Python que representam as tabelas do banco de dados. Cada model = uma tabela. Cada atributo = uma coluna.

### `user.py` — Modelo de Usuario

**Classe `User`** — Representa a tabela `users`:

| Atributo | Tipo | O que e |
|----------|------|---------|
| `id` | UUID | Identificador unico (gerado automaticamente) |
| `name` | String | Nome completo do usuario |
| `email` | String (unico) | E-mail de login |
| `password_hash` | String | Senha criptografada (nunca armazena a senha real) |
| `avatar` | String | URL da foto de perfil |
| `role` | String | Papel: admin, manager, member ou viewer |
| `department` | String | Departamento (ex: Tecnologia) |
| `phone` | String | Telefone |
| `timezone` | String | Fuso horario |
| `status` | String | active, away ou offline |
| `is_active` | Boolean | Se a conta esta ativa |

**Metodos importantes:**

- `set_password(password)` — Recebe a senha em texto puro, criptografa com `generate_password_hash()` e armazena. A senha original NUNCA e salva.
- `check_password(password)` — Compara uma senha digitada com o hash armazenado. Retorna True/False.
- `to_dict()` — Converte o usuario para dicionario (para enviar como JSON). **Nunca inclui a senha.**
- `to_profile_dict()` — Versao mais detalhada com telefone, departamento, etc.

**Classe `UserSettings`** — Representa a tabela `user_settings`:

| Atributo | Tipo | O que e |
|----------|------|---------|
| `theme` | String | Tema: light, dark ou system |
| `language` | String | Idioma: pt-BR, en, es |
| `notifications` | JSON | Configuracoes de notificacao (email, push, etc.) |
| `display_preferences` | JSON | Modo compacto, mostrar avatares, view padrao |

O campo JSON permite guardar dados complexos sem criar tabelas extras. Exemplo do `display_preferences`:
```json
{
  "compactMode": false,
  "showAvatars": true,
  "defaultView": "gantt"
}
```

### `project.py` — Modelo de Projeto

**Classe `Project`** — Representa a tabela `projects`:

| Atributo | Tipo | O que e |
|----------|------|---------|
| `name` | String | Nome do projeto |
| `description` | Text | Descricao detalhada |
| `color` | String | Cor hex (ex: #3b82f6) para visual |
| `status` | String | planning, active, on-hold, completed |
| `progress` | Integer | 0 a 100 (calculado automaticamente) |
| `start_date` | Date | Data de inicio |
| `end_date` | Date | Data de termino |
| `owner_id` | UUID (FK) | ID do usuario dono do projeto |

**Relacionamentos:**
- `tasks` — Lista de tarefas do projeto (1 projeto tem N tarefas)
- `team_members` — Lista de membros da equipe atribuidos ao projeto (N:N)

**Metodo `calculate_progress()`** — Calcula o progresso do projeto automaticamente com base nas tarefas. Se 3 de 6 tarefas estao concluidas = 50%.

### `task.py` — Modelo de Tarefa

**Classe `Task`** — Representa a tabela `tasks`:

| Atributo | Tipo | O que e |
|----------|------|---------|
| `name` | String | Nome da tarefa |
| `description` | Text | Descricao |
| `status` | String | todo, in-progress, review, completed |
| `priority` | String | low, medium, high |
| `progress` | Integer | 0 a 100 |
| `start_date` | Date | Inicio |
| `end_date` | Date | Termino |
| `assignee_id` | UUID (FK) | Quem e responsavel |
| `project_id` | UUID (FK) | A qual projeto pertence |

**`to_dict()`** — Versao simples (para listas)
**`to_dict_detailed()`** — Versao completa (inclui dados do responsavel e do projeto)

### `team_member.py` — Modelo de Membro da Equipe

**Classe `TeamMember`**:

| Atributo | Tipo | O que e |
|----------|------|---------|
| `name` | String | Nome do membro |
| `email` | String (unico) | E-mail |
| `role` | String | Cargo (ex: Desenvolvedor Frontend) |
| `department` | String | Departamento |
| `status` | String | active, away, offline |
| `user_id` | UUID (FK) | Vinculo com conta de usuario (opcional) |

**Tabela `project_members`** — Tabela de associacao entre projetos e membros. Sem classe propria, e apenas uma tabela intermediaria que conecta os dois.

### `department.py` — Modelos de Departamento e Cargo

Duas classes simples: `Department` e `Role`. Ambas tem apenas `id`, `name`, `description` e `created_at`. Sao tabelas de referencia — servem para listar opcoes nos formularios.

---

## 2.5 — Routes (Rotas): `app/routes/`

As rotas sao os "enderecos" da API. Quando o frontend faz uma requisicao, a rota correspondente e executada.

### `auth.py` — Rotas de Autenticacao

**`POST /api/auth/login`** — Login
1. Recebe email e senha
2. Busca usuario no banco por email
3. Verifica se a senha esta correta (`check_password`)
4. Se sim, gera dois tokens JWT (access + refresh)
5. Retorna os tokens e dados do usuario

**`POST /api/auth/register`** — Cadastro
1. Recebe name, email, password
2. Valida: senha minimo 6 caracteres, email nao duplicado
3. Cria novo usuario com `set_password()` (criptografa)
4. Cria configuracoes padrao para o usuario
5. Gera tokens e retorna

**`POST /api/auth/refresh`** — Renovar token
1. Recebe o refresh token
2. Verifica se e valido e nao esta na blacklist
3. Gera novo access token
4. Retorna o novo token

**`POST /api/auth/logout`** — Sair
1. Pega o token atual
2. Adiciona na blacklist (impede uso futuro)
3. Se enviou refresh token, blacklista ele tambem

**`POST /api/auth/change-password`** — Alterar senha
1. Verifica senha atual
2. Valida nova senha (minimo 6 caracteres)
3. Atualiza hash no banco

**`GET /api/auth/me`** — Quem sou eu?
1. Decodifica o token JWT
2. Busca o usuario no banco
3. Retorna dados do usuario

### `users.py` — Rotas de Usuario

**`GET /api/user/profile`** — Busca o perfil do usuario logado

**`PUT /api/user/profile`** — Atualiza o perfil (nome, email, telefone, etc.)

**`GET /api/user/settings`** — Busca as configuracoes (tema, idioma, etc.)

**`PUT /api/user/settings`** — Atualiza as configuracoes

**`POST /api/user/avatar`** — Upload de avatar:
1. Recebe o arquivo (imagem)
2. Valida extensao (png, jpg, etc.) e tamanho (max 5MB)
3. Gera nome unico com UUID (para evitar conflitos)
4. Salva na pasta `uploads/avatars/`
5. Remove o avatar antigo se existir
6. Atualiza a URL no banco
7. Retorna o perfil atualizado

**`GET /api/uploads/avatars/<filename>`** — Serve o arquivo de avatar (rota publica)

### `projects.py` — Rotas de Projetos

**`GET /api/projects`** — Lista projetos
- Aceita filtro `?status=active` para filtrar por status
- Aceita `?page=1&limit=10` para paginacao
- Retorna lista paginada

**`POST /api/projects`** — Cria projeto (precisa ser manager ou admin)
- Recebe: name, description, color, status, start_date, end_date
- Valida dados (datas, status valido, etc.)
- Cria no banco com o usuario logado como owner

**`PUT /api/projects/:id`** — Atualiza projeto

**`DELETE /api/projects/:id`** — Exclui projeto (somente admin)

**`POST /api/projects/:id/members/:memberId`** — Adiciona membro ao projeto

**`DELETE /api/projects/:id/members/:memberId`** — Remove membro do projeto

### `tasks.py` — Rotas de Tarefas

Similar a projetos, mas com filtros adicionais:
- `?projectId=xxx` — Tarefas de um projeto especifico
- `?status=todo` — Filtrar por status
- `?assigneeId=xxx` — Tarefas de um membro
- `?priority=high` — Filtrar por prioridade

**`PATCH /api/tasks/:id/status`** — Atualiza so o status (rapido)
**`PATCH /api/tasks/:id/progress`** — Atualiza so o progresso (rapido)

Quando uma tarefa muda de status para "completed", o progresso vai automaticamente para 100%. Quando o progresso chega a 100%, o status vira "completed".

### `team.py` — Rotas de Equipe

CRUD completo de membros. A rota `GET /api/team/departments` retorna a lista de departamentos existentes para popular selects no frontend.

---

## 2.6 — Services (Servicos): `app/services/`

Os services contem a **logica de negocio**. As rotas recebem a requisicao, os services processam. Isso separa "o que chega" de "o que acontece".

### `user_service.py`

**Classe `UserService`:**

- `authenticate(email, password)` — Busca usuario por email, verifica senha. Retorna o usuario se correto, None se errado.
- `get_by_id(id)` — Busca usuario pelo ID
- `get_by_email(email)` — Busca usuario pelo email
- `create(data)` — Cria usuario: sanitiza inputs, criptografa senha, salva no banco
- `update(id, data)` — Atualiza usuario: sanitiza dados, aplica mudancas
- `delete(id)` — Desativa usuario (nao apaga, muda `is_active` para False)
- `sanitize_user_data(data)` — Limpa os dados de entrada para evitar ataques XSS. Remove tags HTML de strings.

**Classe `UserSettingsService`:**

- `get_or_create(user_id)` — Busca settings do usuario. Se nao existir, cria com valores padrao.
- `update(user_id, data)` — Atualiza settings. Faz merge inteligente dos campos JSON (nao sobrescreve tudo, so o que mudou).

### `project_service.py`

**Classe `ProjectService`:**

- `get_all(status, page, limit)` — Lista projetos com filtro e paginacao
- `create(data, owner_id)` — Cria projeto: sanitiza dados, valida datas, associa ao owner
- `update(id, data)` — Atualiza: valida dados, recalcula progresso se necessario
- `delete(id)` — Exclui projeto e todas as tarefas associadas (cascade)
- `add_team_member(project_id, member_id)` — Adiciona membro ao projeto (verifica duplicatas)
- `remove_team_member(project_id, member_id)` — Remove membro do projeto

### `task_service.py`

**Classe `TaskService`:**

- `get_all(filters)` — Lista tarefas com todos os filtros possiveis
- `create(data)` — Cria tarefa, atualiza progresso do projeto automaticamente
- `update(id, data)` — Atualiza tarefa. Se mudou status/progresso, sincroniza (completed = 100%)
- `delete(id)` — Exclui tarefa, recalcula progresso do projeto
- `update_status(id, status)` — Atalho: so muda o status
- `update_progress(id, progress)` — Atalho: so muda o progresso

### `team_service.py`

**Classe `TeamService`:**

- `get_all(department, status, page, limit)` — Lista membros com filtros
- `create(data)` — Cria membro (valida email unico)
- `update(id, data)` — Atualiza membro
- `delete(id)` — Exclui membro

---

## 2.7 — Utils (Utilitarios): `app/utils/`

### `response.py` — Formatacao de respostas

Todas as respostas da API seguem o mesmo formato. Essas funcoes garantem consistencia:

- **`api_response(data, message, status_code)`** — Resposta de sucesso
  ```json
  { "success": true, "data": {...}, "message": "OK" }
  ```

- **`paginated_response(data, page, limit, total)`** — Resposta com paginacao
  ```json
  { "success": true, "data": [...], "pagination": { "page": 1, "limit": 10, "total": 47 } }
  ```

- **`error_response(message, status_code, errors)`** — Resposta de erro
  ```json
  { "success": false, "data": null, "message": "Erro descritivo" }
  ```

### `rbac.py` — Controle de Permissoes

Este e um dos arquivos mais importantes. Define QUEM pode fazer O QUE.

**Enum `Role`** — Os 4 papeis:
```python
ADMIN = 'admin'      # Pode tudo
MANAGER = 'manager'  # Gerencia projetos e equipe
MEMBER = 'member'    # Trabalha em tarefas
VIEWER = 'viewer'    # So visualiza
```

**Enum `Permission`** — Permissoes granulares:
```python
CREATE_PROJECT = 'create_project'
UPDATE_PROJECT = 'update_project'
DELETE_PROJECT = 'delete_project'
CREATE_TASK = 'create_task'
# ... etc
```

**`ROLE_PERMISSIONS`** — Dicionario que mapeia cada papel as suas permissoes. O admin tem todas, o viewer nao tem nenhuma de escrita.

**Decoradores** (funcoes especiais que "embrulham" outras funcoes):

- `@require_auth` — Verifica se o usuario esta logado. Se nao, retorna 401.
- `@require_role(Role.MANAGER)` — Verifica se o usuario tem o papel minimo. Se um viewer tentar, retorna 403.
- `@require_permission(Permission.CREATE_PROJECT)` — Verifica permissao especifica.
- `@require_admin` — Atalho para `@require_role(Role.ADMIN)`
- `@require_manager` — Atalho para `@require_role(Role.MANAGER)`

Exemplo de como uma rota usa decoradores:
```python
@projects_bp.route('/projects', methods=['POST'])
@require_auth          # Precisa estar logado
@require_manager       # Precisa ser manager ou admin
def create_project():
    # ... codigo da rota
```

### `validators.py` — Validacao de entrada

Decoradores que validam os dados ANTES de processar:

- `@validate_json` — Garante que a requisicao tem corpo JSON valido
- `@validate_required_fields(['name', 'email'])` — Garante que os campos obrigatorios existem
- `@validate_enum_field('status', ['active', 'away'])` — Garante que o valor e um dos permitidos
- `@validate_email('email')` — Garante formato de email valido
- `@validate_date_format('start_date')` — Garante formato YYYY-MM-DD
- `@validate_progress('progress')` — Garante numero entre 0 e 100

Se a validacao falhar, a rota NEM EXECUTA — retorna erro 400 imediatamente.

### `token_blacklist.py` — Blacklist de tokens

Quando um usuario faz logout, o token dele e adicionado a uma lista negra. Se alguem tentar usar esse token depois, o sistema rejeita.

**Classe `TokenBlacklist`:**
- `add(jti, expiration)` — Adiciona token a blacklist. `jti` e o identificador unico do token.
- `is_blacklisted(jti)` — Verifica se o token esta na blacklist.
- `revoke_all_user_tokens(user_id)` — Invalida TODOS os tokens de um usuario (ex: mudanca de senha).

Suporta Redis (producao) ou dicionario em memoria (desenvolvimento).

---

# PARTE 3 — FRONTEND (O SALAO)

O frontend e feito em **TypeScript** usando **Next.js** (framework baseado em React).

---

## 3.1 — O que e React?

React e uma biblioteca que permite construir interfaces dividindo tudo em **componentes**. Um componente e como um bloco de LEGO — uma peca reutilizavel de interface.

Exemplo: o `Button` e um componente. O `Header` e um componente. O `ProjectCard` e um componente. Voce combina componentes menores pra fazer componentes maiores.

## 3.2 — O que e Next.js?

Next.js e um framework que roda em cima do React. Ele adiciona:
- **Roteamento por arquivo** — Cada arquivo em `app/` vira uma pagina automaticamente
- **Server-Side Rendering** — Paginas podem ser renderizadas no servidor
- **Otimizacoes** — Imagens, fontes, bundling automatico

## 3.3 — O que e TypeScript?

TypeScript e JavaScript com **tipos**. Em vez de:
```javascript
function soma(a, b) { return a + b }  // JavaScript: a e b podem ser qualquer coisa
```
Voce escreve:
```typescript
function soma(a: number, b: number): number { return a + b }  // TypeScript: a e b DEVEM ser numeros
```
Isso previne erros — se voce tentar passar uma string, o editor ja avisa antes de rodar.

---

## 3.4 — Layout raiz: `app/layout.tsx`

Este arquivo e o "esqueleto" de TODAS as paginas. Tudo que esta aqui aparece em qualquer pagina.

```tsx
<html lang="pt-BR">
  <body>
    <ThemeProvider>        {/* Controla tema claro/escuro */}
      <Toaster>            {/* Sistema de notificacoes toast */}
        <AuthProvider>     {/* Controla autenticacao */}
          <SettingsProvider>  {/* Controla preferencias */}
            {children}     {/* Aqui entra o conteudo da pagina */}
          </SettingsProvider>
        </AuthProvider>
      </Toaster>
    </ThemeProvider>
  </body>
</html>
```

**Providers** sao componentes que "envolvem" a aplicacao e fornecem dados globais. Qualquer componente filho pode acessar os dados do provider.

---

## 3.5 — Pagina principal: `app/page.tsx`

Este arquivo e a pagina `/`. Ele faz duas coisas:

1. **Se o usuario NAO esta logado** → Mostra a Landing Page
2. **Se o usuario ESTA logado** → Mostra o Dashboard

**Quando logado, o Dashboard:**
- Carrega tarefas, projetos e membros da API (`loadDashboardData`)
- Mostra cards de estatisticas (`StatsCards`)
- Mostra o grafico Gantt (`GanttChart`)
- Permite criar, editar e excluir tarefas via dialogs

**Funcoes importantes:**

- `loadDashboardData()` — Faz 3 chamadas paralelas a API (tarefas, membros, projetos). Usa `Promise.all` para buscar tudo ao mesmo tempo.
- `handleSaveTask(data)` — Cria ou atualiza uma tarefa via API. Se tem ID, atualiza. Se nao tem, cria.
- `handleDeleteTask(id)` — Exclui uma tarefa via API.
- `handleTaskClick(task)` — Abre o dialog de detalhes da tarefa.
- `handleNewTask()` — Abre o dialog de criacao de tarefa.

---

## 3.6 — Paginas de autenticacao

### `app/login/page.tsx`

Formulario com email e senha. Ao submeter:
1. Chama `login(email, password)` do AuthContext
2. Se sucesso, redireciona para `/`
3. Se erro, mostra mensagem

### `app/register/page.tsx`

Formulario com nome, email, senha e confirmar senha. Ao submeter:
1. Valida que as senhas sao iguais
2. Chama a API `POST /api/auth/register`
3. Se sucesso, redireciona para `/login`

---

## 3.7 — Contexts (Estado Global): `contexts/`

### `auth-context.tsx` — Contexto de Autenticacao

Pense neste arquivo como o "gerente de seguranca" da aplicacao. Ele sabe quem esta logado e controla o acesso.

**Interface `User`** — Define os dados do usuario:
```typescript
interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'manager' | 'member' | 'viewer'
  avatar?: string    // ? = campo opcional
}
```

**`AuthProvider`** — Componente que envolve toda a app:

- **Estado `user`** — Armazena os dados do usuario logado (ou null se nao logado)
- **Estado `isLoading`** — True enquanto verifica se tem token valido
- **Estado `isAuthenticated`** — True se user nao e null

**Funcoes expostas:**

- `login(email, password)` — Envia credenciais para a API, salva tokens no localStorage, atualiza o estado `user`
- `logout()` — Chama API de logout, limpa localStorage, redireciona para /login
- `refreshUser()` — Busca dados atualizados do usuario na API
- `checkAuth()` — Executada ao abrir o site. Verifica se tem token salvo, se sim busca os dados do usuario. Se o token expirou, limpa tudo.

**Hook `useAuth()`** — Funcao que qualquer componente chama para acessar os dados:
```typescript
const { user, login, logout, isAuthenticated } = useAuth()
```

### `settings-context.tsx` — Contexto de Preferencias

Gerencia as preferencias do usuario (tema, modo compacto, avatares).

**`SettingsProvider`** — Usa SWR para buscar settings da API:
- Se o usuario esta logado, busca `GET /api/user/settings`
- Armazena em cache (nao busca de novo a cada pagina)
- Re-busca quando `mutateSettings()` e chamado

**Funcoes expostas:**

- `settings` — Dados das preferencias
- `updateSettings(updates)` — Atualiza preferencias na API
- `mutateSettings()` — Forca re-busca dos dados (apos salvar na pagina de settings)

---

## 3.8 — Tipos: `lib/types.ts`

Define TODAS as interfaces TypeScript do projeto. Cada interface e como um "contrato" — diz exatamente que formato os dados devem ter.

```typescript
interface Task {
  id: string
  name: string
  status: 'todo' | 'in-progress' | 'review' | 'completed'
  priority: 'low' | 'medium' | 'high'
  progress: number
  startDate: string
  endDate: string
  assigneeId?: string
  projectId?: string
}
```

Se voce tentar criar uma tarefa sem `name`, o TypeScript da erro ANTES de rodar. Isso previne muitos bugs.

Outras interfaces importantes:
- `Project` — Dados de projeto
- `TeamMember` — Dados de membro da equipe
- `UserProfile` — Perfil do usuario
- `UserSettings` — Configuracoes do usuario
- `ApiResponse<T>` — Formato padrao de resposta da API (generico)
- `CreateTaskInput` — Dados necessarios para criar uma tarefa

---

## 3.9 — Configuracao da API: `lib/api-config.ts`

Este arquivo e o "tradutor" entre frontend e backend.

**Constante `API_URL`** — Endereco base da API: `http://localhost:5000/api`

**Funcao `apiFetch(endpoint, options)`** — Funcao central que faz TODAS as chamadas a API:

1. Monta a URL completa (`API_URL + endpoint`)
2. Adiciona headers: `Content-Type: application/json` e `Authorization: Bearer <token>`
3. Se o body e FormData (upload), remove o Content-Type (o browser define automaticamente)
4. Faz a requisicao com `fetch()`
5. Se recebeu 401 (token expirado):
   - Tenta renovar o token com o refresh token
   - Se conseguiu, repete a requisicao original com o novo token
   - Se nao conseguiu, redireciona para /login
6. Se recebeu outro erro, lanca `ApiError` com o codigo e mensagem

**Classe `ApiError`** — Erro personalizado com:
- `code` — Codigo do erro (UNAUTHORIZED, FORBIDDEN, NOT_FOUND, etc.)
- `status` — HTTP status code (401, 403, 404, etc.)
- `message` — Mensagem descritiva

**`ERROR_CODES`** — Constantes para cada tipo de erro:
```typescript
UNAUTHORIZED = 'UNAUTHORIZED'    // Nao autenticado
FORBIDDEN = 'FORBIDDEN'          // Sem permissao
NOT_FOUND = 'NOT_FOUND'          // Nao encontrado
VALIDATION = 'VALIDATION'       // Dados invalidos
```

---

## 3.10 — Servicos: `lib/services/`

Cada service encapsula as chamadas API de um modulo. Em vez de escrever `apiFetch('/tasks', { method: 'POST', ... })` em cada componente, voce chama `createTask(data)`.

### `task-service.ts`

```typescript
getTasks(filters?)        // GET /api/tasks
getTask(id)               // GET /api/tasks/:id
createTask(data)          // POST /api/tasks
updateTask(data)          // PUT /api/tasks/:id
deleteTask(id)            // DELETE /api/tasks/:id
updateTaskStatus(id, s)   // PATCH /api/tasks/:id/status
updateTaskProgress(id, p) // PATCH /api/tasks/:id/progress
```

### `project-service.ts`

```typescript
getProjects(filters?)     // GET /api/projects
getProject(id)            // GET /api/projects/:id
createProject(data)       // POST /api/projects
updateProject(data)       // PUT /api/projects/:id
deleteProject(id)         // DELETE /api/projects/:id
```

### `team-service.ts`

```typescript
getTeamMembers(filters?)  // GET /api/team
createTeamMember(data)    // POST /api/team
updateTeamMember(data)    // PUT /api/team/:id
deleteTeamMember(id)      // DELETE /api/team/:id
```

### `settings-service.ts`

```typescript
getUserProfile()          // GET /api/user/profile
updateUserProfile(data)   // PUT /api/user/profile
getUserSettings()         // GET /api/user/settings
updateUserSettings(data)  // PUT /api/user/settings
changePassword(old, new)  // POST /api/auth/change-password
uploadAvatar(file)        // POST /api/user/avatar (FormData)
```

---

## 3.11 — Permissoes no Frontend: `lib/permissions.ts`

Funcoes simples que verificam se um papel pode fazer algo:

```typescript
canCreateProject('member')  // false (so manager+ pode)
canCreateProject('manager') // true
canCreateTask('viewer')     // false (so member+ pode)
canCreateTask('member')     // true
canManageTeam('admin')      // true
```

Essas funcoes sao usadas nos componentes para **esconder/mostrar botoes**. Se o usuario e viewer, o botao "Criar Projeto" nem aparece.

**IMPORTANTE:** Isso e apenas visual. A protecao REAL esta no backend (decoradores RBAC). Mesmo que alguem hackeie o frontend e force um botao a aparecer, o backend vai rejeitar a requisicao.

---

## 3.12 — Componentes de Layout: `components/layout/`

### `dashboard-layout.tsx`

O "esqueleto" de todas as paginas autenticadas. Organiza:
```
┌──────────────────────────────────┐
│ Sidebar │ Header                 │
│         │────────────────────────│
│  Menu   │                        │
│  lateral│   {children}           │
│         │   (conteudo da pagina) │
│         │                        │
└──────────────────────────────────┘
```

Tambem aplica o **modo compacto** — se ativo nas preferencias, adiciona a classe CSS `compact` que reduz espacamentos.

### `header.tsx`

Barra superior com:
- Botao "Nova Tarefa" (visivel por permissao)
- Busca global (Ctrl+K) com resultados de projetos, tarefas e membros
- Sino de notificacoes (geradas a partir de dados reais)
- Menu do usuario com avatar, nome e opcoes (Settings, Logout)

**Busca global:** Quando o usuario digita, filtra projetos, tarefas e membros pelo nome. Ao clicar em um resultado, navega para a pagina correspondente.

**Avatares:** Respeita a preferencia `showAvatars` — se desligada, mostra apenas iniciais.

### `sidebar.tsx`

Menu lateral com links de navegacao:
- Dashboard (/)
- Projetos (/projects)
- Equipe (/team)
- Admin (/admin) — so aparece para admins
- Configuracoes (/settings)

Tem botao de recolher que transforma o sidebar em icones apenas.

---

## 3.13 — Componentes do Gantt: `components/gantt/`

### `gantt-chart.tsx`

O componente mais complexo do projeto. Renderiza o grafico Gantt.

**O que recebe (props):**
- `tasks` — Lista de tarefas
- `teamMembers` — Lista de membros (para mostrar nomes)
- `onTaskClick` — Funcao chamada ao clicar numa tarefa
- `onTaskEdit` — Funcao chamada ao querer editar

**Como funciona:**
1. `calculateDateRange(tasks)` — Calcula a data mais antiga e mais recente entre todas as tarefas. Esse e o range do grafico.
2. Gera o header do timeline (datas no topo)
3. Para cada tarefa, calcula a posicao horizontal (qual % da largura corresponde ao inicio/fim)
4. Renderiza barras coloridas por status
5. Linha vermelha vertical marca "hoje"

**Modos de visualizacao:**
- `day` — Cada coluna e um dia
- `week` — Cada coluna e uma semana
- `month` — Cada coluna e um mes

### `gantt-task-bar.tsx`

Cada barra individual no grafico. Recebe a tarefa e as posicoes calculadas. Mostra nome e progresso.

### `gantt-tooltip.tsx`

Popup que aparece quando o mouse passa sobre uma barra. Mostra: nome, projeto, responsavel, datas, status e progresso.

---

## 3.14 — Componentes de Projeto: `components/projects/`

### `project-card.tsx`

Card visual que mostra um projeto com:
- Nome e descricao
- Badge de status com cor (ex: "Ativo" em verde)
- Barra de progresso
- Datas de inicio/termino
- Numero de membros
- Menu de contexto (editar, excluir) — visivel por permissao

### `project-form-dialog.tsx`

Dialog (popup) para criar ou editar projetos. Campos:
- Nome, descricao
- Status (select com opcoes)
- Datas de inicio e termino
- Cor do projeto

### `project-detail-dialog.tsx`

Dialog que mostra detalhes completos de um projeto:
- Status, progresso, datas
- Resumo de tarefas (concluidas, em progresso, a fazer)
- Lista de membros da equipe

---

## 3.15 — Componentes de Tarefa: `components/tasks/`

### `task-form-dialog.tsx`

Dialog para criar/editar tarefas. Campos:
- Nome, descricao
- Status (A Fazer, Em Progresso, Em Revisao, Concluida)
- Prioridade (Baixa, Media, Alta)
- Projeto (select populado da API)
- Responsavel (select populado da API)
- Datas de inicio e termino
- Progresso (slider 0-100) — so aparece ao editar

### `task-detail-dialog.tsx`

Dialog que mostra detalhes de uma tarefa:
- Todas as informacoes da tarefa
- Nome e avatar do responsavel
- Nome do projeto
- Botao "Editar Tarefa" (visivel por permissao)

---

## 3.16 — Componentes de Equipe: `components/team/`

### `team-member-card.tsx`

Card visual de um membro com:
- Avatar (ou iniciais se avatares desligados)
- Nome e cargo
- Email clicavel (abre mailto)
- Departamento
- Badge de status (Ativo/Ausente/Offline) com cor
- Data de ingresso
- Menu de contexto (editar, email, remover)

### `team-member-form-dialog.tsx`

Dialog para criar/editar membros. Carrega departamentos e cargos da API para popular os selects.

---

## 3.17 — Componentes de Configuracao: `components/settings/`

### `profile-section.tsx`

Formulario de perfil com campos editaveis. Tem botao de camera no avatar para upload.

### `preferences-section.tsx`

Opcoes de preferencias:
- Tema (Claro/Escuro/Sistema) — aplica imediatamente via `useTheme()`
- Visualizacao padrao (Gantt/Lista/Quadro)
- Modo compacto (toggle) — reduz espacamentos globalmente
- Mostrar avatares (toggle) — esconde/mostra fotos

### `password-section.tsx`

Formulario de alteracao de senha: senha atual + nova senha + confirmar.

### `notifications-section.tsx`

Toggles de notificacao: email, push, lembretes, atualizacoes.

---

## 3.18 — Landing Page: `components/landing/landing-page.tsx`

Pagina publica para visitantes nao logados. Secoes:

1. **Header** — Logo + botoes Entrar/Cadastrar
2. **Hero** — Titulo grande + CTAs
3. **Preview** — Mock visual do dashboard (barras Gantt fake, stats, sidebar)
4. **Stats** — Numeros destacados (Gantt, 4 niveis, 100% responsivo, PT-BR)
5. **Features** — 4 cards explicando funcionalidades
6. **Como funciona** — 3 passos (Cadastro → Projetos → Acompanhamento)
7. **CTA final** — "Pronto para comecar?"
8. **Footer** — Logo + copyright

---

## 3.19 — Estilos: `app/globals.css`

Define as cores e variaveis CSS para toda a aplicacao.

**`:root`** — Variaveis do tema claro (fundos claros, textos escuros)
**`.dark`** — Variaveis do tema escuro (fundos escuros, textos claros)

O `next-themes` adiciona a classe `dark` no `<html>` quando o tema escuro esta ativo. O CSS muda todas as cores automaticamente.

**`.compact`** — Quando modo compacto esta ativo, reduz paddings e gaps globalmente:
```css
.compact .p-6 { padding: 0.75rem; }
.compact .gap-4 { gap: 0.5rem; }
```

---

## 3.20 — Utilitarios do Gantt: `lib/gantt-utils.ts`

Funcoes matematicas para calcular o Gantt:

- `calculateDateRange(tasks)` — Encontra a data mais antiga e mais recente. Adiciona margem de 1 dia em cada lado.
- `generateTimelineHeader(start, days)` — Gera array de datas para o header.
- `calculateTaskPosition(task, start, days)` — Calcula posicao e largura de cada barra em percentual.
- `generateWeekTimeline(start, days)` — Agrupa dias em semanas.
- `generateMonthTimeline(start, days)` — Agrupa dias em meses.
- `getTodayPositionByViewMode(start, days, mode)` — Calcula onde a linha "hoje" deve ficar.

---

# PARTE 4 — COMO TUDO SE CONECTA

## Fluxo completo: Login

```
1. Usuario digita email e senha na tela de login
2. login/page.tsx chama login() do AuthContext
3. AuthContext chama apiFetch('/auth/login', { method: 'POST', body: {email, senha} })
4. apiFetch envia para http://localhost:5000/api/auth/login
5. Flask recebe na rota POST /api/auth/login (auth.py)
6. Rota chama UserService.authenticate(email, password)
7. Service busca usuario no banco (User.query.filter_by(email=email))
8. Service verifica senha (user.check_password(password))
9. Rota gera tokens JWT (create_access_token, create_refresh_token)
10. Retorna JSON: { success: true, data: { accessToken, refreshToken, user } }
11. apiFetch recebe a resposta
12. AuthContext salva tokens no localStorage
13. AuthContext atualiza estado user
14. isAuthenticated vira true
15. page.tsx detecta que isAuthenticated = true
16. Renderiza o Dashboard em vez da Landing Page
17. Dashboard chama loadDashboardData()
18. 3 chamadas paralelas: getTasks(), getTeamMembers(), getProjects()
19. Dados chegam, StatsCards e GanttChart renderizam
```

## Fluxo completo: Criar tarefa

```
1. Usuario clica "Nova Tarefa" no header
2. TaskFormDialog abre com campos vazios
3. Usuario preenche e clica "Criar Tarefa"
4. page.tsx chama handleSaveTask(data)
5. handleSaveTask chama createTask(data) do task-service
6. task-service chama apiFetch('/tasks', { method: 'POST', body: data })
7. Flask recebe na rota POST /api/tasks (tasks.py)
8. Decorador @require_auth verifica o token
9. Decorador @require_permission(CREATE_TASK) verifica permissao
10. Rota valida dados (campos obrigatorios, formato de datas)
11. Rota chama TaskService.create(data)
12. Service sanitiza dados, cria Task no banco
13. Service atualiza progresso do projeto associado
14. Retorna tarefa criada em JSON
15. Frontend recebe, fecha dialog, recarrega dados
16. GanttChart renderiza com a nova tarefa
```

---

# PARTE 5 — GLOSSARIO

| Termo | Significado |
|-------|-------------|
| **API** | Interface de Programacao de Aplicacao — conjunto de endpoints que o frontend usa para comunicar com o backend |
| **Blueprint** | No Flask, forma de organizar rotas em modulos separados |
| **CORS** | Cross-Origin Resource Sharing — permite que o frontend (porta 3000) acesse o backend (porta 5000) |
| **CRUD** | Create, Read, Update, Delete — as 4 operacoes basicas de dados |
| **Decorator** | No Python, funcao que envolve outra funcao para adicionar comportamento (ex: verificar permissao antes de executar) |
| **Endpoint** | Um endereco especifico da API (ex: GET /api/tasks) |
| **FK (Foreign Key)** | Chave estrangeira — campo que referencia o ID de outra tabela |
| **Hook** | No React, funcoes especiais (useState, useEffect, useContext) que adicionam funcionalidade a componentes |
| **JWT** | JSON Web Token — token de autenticacao que carrega dados do usuario codificados |
| **Middleware** | Codigo que executa ENTRE a requisicao chegar e a resposta sair |
| **ORM** | Object-Relational Mapping — traduz objetos Python para SQL automaticamente |
| **Props** | Propriedades passadas para um componente React (como argumentos de uma funcao) |
| **Provider** | Componente React que fornece dados globais para todos os filhos |
| **SWR** | Stale-While-Revalidate — biblioteca que faz cache de dados e re-busca automaticamente |
| **State** | Estado — dados que podem mudar e fazem o componente re-renderizar |
| **UUID** | Identificador Unico Universal — string aleatoria usada como ID (ex: 550e8400-e29b-41d4-a716-446655440000) |

---

*Este guia cobre todos os arquivos e funcoes do projeto ProjectFlow. Releia as partes que nao entendeu — a repeticao e parte do aprendizado.*
