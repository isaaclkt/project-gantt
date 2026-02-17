/**
 * ProjectFlow Gantt - Main Application
 * Lógica principal da aplicação
 */

// ============================================
// Estado Global
// ============================================
const App = {
    projects: [],
    tasks: [],
    currentView: 'dashboard',
    ganttChart: null,
    deleteCallback: null,
};

// ============================================
// Inicialização
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Event Listeners
    setupNavigation();
    setupModals();
    setupForms();
    setupFilters();
    setupTheme();

    // Carrega dados iniciais
    await loadDashboard();
    await loadProjects();
}

// ============================================
// Navegação
// ============================================
function setupNavigation() {
    // Menu items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            navigateTo(view);
        });
    });

    // Menu toggle (mobile)
    document.getElementById('menuToggle').addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('active');
    });

    // Botão novo projeto
    document.getElementById('btnNewProject').addEventListener('click', () => {
        openProjectModal();
    });

    // Botão nova tarefa
    document.getElementById('btnNewTask').addEventListener('click', () => {
        openTaskModal();
    });

    // Botão hoje no Gantt
    document.getElementById('btnToday').addEventListener('click', () => {
        if (App.ganttChart) {
            App.ganttChart.scrollToToday();
        }
    });

    // Zoom do Gantt
    document.querySelectorAll('[data-zoom]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-zoom]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (App.ganttChart) {
                App.ganttChart.setZoom(btn.dataset.zoom);
            }
        });
    });
}

function navigateTo(view) {
    App.currentView = view;

    // Atualiza menu ativo
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === view);
    });

    // Atualiza título
    const titles = {
        dashboard: 'Dashboard',
        projects: 'Projetos',
        gantt: 'Gráfico de Gantt',
        tasks: 'Tarefas'
    };
    document.getElementById('pageTitle').textContent = titles[view] || 'Dashboard';

    // Mostra view correspondente
    document.querySelectorAll('.view').forEach(v => {
        v.classList.toggle('active', v.id === `${view}View`);
    });

    // Carrega dados específicos da view
    switch (view) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'projects':
            renderProjects();
            break;
        case 'gantt':
            loadGantt();
            break;
        case 'tasks':
            loadTasks();
            break;
    }

    // Fecha sidebar no mobile
    document.querySelector('.sidebar').classList.remove('active');
}

// ============================================
// Dashboard
// ============================================
async function loadDashboard() {
    try {
        const [metrics, projects] = await Promise.all([
            API.getDashboard(),
            API.getProjects()
        ]);

        App.projects = projects;

        // Atualiza métricas
        document.getElementById('totalProjects').textContent = metrics.total_projects;
        document.getElementById('totalTasks').textContent = metrics.total_tasks;
        document.getElementById('doingTasks').textContent = metrics.doing;
        document.getElementById('doneTasks').textContent = metrics.done;
        document.getElementById('overdueTasks').textContent = metrics.overdue;
        document.getElementById('completionRate').textContent = `${metrics.completion_rate}%`;

        // Atualiza gráfico de barras
        updateStatusChart(metrics);

        // Atualiza projetos recentes
        renderRecentProjects(projects.slice(0, 5));

        // Atualiza selects de projetos
        updateProjectSelects(projects);

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function updateStatusChart(metrics) {
    const maxValue = Math.max(metrics.todo, metrics.doing, metrics.review, metrics.done, 1);

    const bars = {
        todo: metrics.todo,
        doing: metrics.doing,
        review: metrics.review,
        done: metrics.done
    };

    Object.entries(bars).forEach(([status, value]) => {
        const bar = document.querySelector(`.chart-bar.${status}`);
        if (bar) {
            const height = Math.max(30, (value / maxValue) * 150);
            bar.style.height = `${height}px`;
            bar.querySelector('.bar-value').textContent = value;
        }
    });
}

function renderRecentProjects(projects) {
    const container = document.getElementById('recentProjects');

    if (projects.length === 0) {
        container.innerHTML = '<p class="empty-state">Nenhum projeto encontrado</p>';
        return;
    }

    container.innerHTML = projects.map(project => `
        <div class="project-item" data-project-id="${project.id}">
            <div class="project-icon">
                <i class="fas fa-folder"></i>
            </div>
            <div class="project-info">
                <div class="project-name">${escapeHtml(project.name)}</div>
                <div class="project-meta">${project.task_count} tarefas</div>
            </div>
            <div class="project-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                </div>
                <div class="progress-text">${project.progress}%</div>
            </div>
        </div>
    `).join('');

    // Click handler para ver projeto no Gantt
    container.querySelectorAll('.project-item').forEach(item => {
        item.addEventListener('click', () => {
            const projectId = item.dataset.projectId;
            document.getElementById('projectSelect').value = projectId;
            navigateTo('gantt');
        });
    });
}

// ============================================
// Projetos
// ============================================
async function loadProjects() {
    try {
        App.projects = await API.getProjects();
        renderProjects();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function renderProjects() {
    const container = document.getElementById('projectsGrid');

    if (App.projects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>Nenhum projeto encontrado</p>
                <button class="btn btn-primary" onclick="openProjectModal()" style="margin-top: 1rem;">
                    <i class="fas fa-plus"></i> Criar Projeto
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = App.projects.map(project => `
        <div class="project-card" data-project-id="${project.id}">
            <div class="project-card-header">
                <h3>${escapeHtml(project.name)}</h3>
                <p>${escapeHtml(project.description || 'Sem descrição')}</p>
            </div>
            <div class="project-card-body">
                <div class="project-stats">
                    <div class="project-stat">
                        <div class="project-stat-value">${project.task_count}</div>
                        <div class="project-stat-label">Tarefas</div>
                    </div>
                    <div class="project-stat">
                        <div class="project-stat-value">${project.completed_tasks}</div>
                        <div class="project-stat-label">Concluídas</div>
                    </div>
                    <div class="project-stat">
                        <div class="project-stat-value">${project.progress}%</div>
                        <div class="project-stat-label">Progresso</div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                </div>
            </div>
            <div class="project-card-footer">
                <button class="btn btn-sm" onclick="viewProjectGantt(${project.id})">
                    <i class="fas fa-chart-gantt"></i> Gantt
                </button>
                <button class="btn btn-sm" onclick="openProjectModal(${project.id})">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button class="btn btn-sm btn-danger" onclick="confirmDeleteProject(${project.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function viewProjectGantt(projectId) {
    document.getElementById('projectSelect').value = projectId;
    navigateTo('gantt');
}

function openProjectModal(projectId = null) {
    const modal = document.getElementById('projectModal');
    const form = document.getElementById('projectForm');
    const title = document.getElementById('projectModalTitle');

    form.reset();
    document.getElementById('projectId').value = '';

    if (projectId) {
        title.textContent = 'Editar Projeto';
        const project = App.projects.find(p => p.id === projectId);
        if (project) {
            document.getElementById('projectId').value = project.id;
            document.getElementById('projectName').value = project.name;
            document.getElementById('projectDescription').value = project.description || '';
        }
    } else {
        title.textContent = 'Novo Projeto';
    }

    modal.classList.add('active');
}

async function saveProject(e) {
    e.preventDefault();

    const projectId = document.getElementById('projectId').value;
    const data = {
        name: document.getElementById('projectName').value,
        description: document.getElementById('projectDescription').value
    };

    try {
        if (projectId) {
            await API.updateProject(projectId, data);
            showToast('Projeto atualizado com sucesso!', 'success');
        } else {
            await API.createProject(data);
            showToast('Projeto criado com sucesso!', 'success');
        }

        closeModal('projectModal');
        await loadProjects();
        await loadDashboard();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function confirmDeleteProject(projectId) {
    const project = App.projects.find(p => p.id === projectId);
    document.getElementById('confirmMessage').textContent =
        `Tem certeza que deseja excluir o projeto "${project?.name}"? Todas as tarefas serão excluídas.`;

    App.deleteCallback = async () => {
        try {
            await API.deleteProject(projectId);
            showToast('Projeto excluído com sucesso!', 'success');
            closeModal('confirmModal');
            await loadProjects();
            await loadDashboard();
        } catch (error) {
            showToast(error.message, 'error');
        }
    };

    document.getElementById('confirmModal').classList.add('active');
}

// ============================================
// Gantt
// ============================================
async function loadGantt() {
    const projectSelect = document.getElementById('projectSelect');
    const projectId = projectSelect.value;

    try {
        let tasks;
        if (projectId) {
            tasks = await API.getProjectTasks(projectId);
        } else {
            tasks = await API.getTasks();
        }

        renderGantt(tasks);

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function renderGantt(tasks) {
    const container = document.getElementById('ganttChart');

    if (!App.ganttChart) {
        App.ganttChart = new GanttChart(container, {
            onTaskClick: (task) => {
                openTaskModal(task.id);
            },
            onTaskEdit: (task) => {
                openTaskModal(task.id);
            }
        });
    }

    App.ganttChart.setTasks(tasks);
}

// ============================================
// Tarefas
// ============================================
async function loadTasks() {
    const projectFilter = document.getElementById('filterProject').value;
    const statusFilter = document.getElementById('filterStatus').value;

    try {
        let tasks;
        if (projectFilter) {
            tasks = await API.getProjectTasks(projectFilter);
        } else {
            tasks = await API.getTasks();
        }

        // Filtro de status
        if (statusFilter) {
            tasks = tasks.filter(t => t.status === statusFilter);
        }

        App.tasks = tasks;
        renderTasksTable(tasks);

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function renderTasksTable(tasks) {
    const tbody = document.getElementById('tasksTableBody');

    if (tasks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    Nenhuma tarefa encontrada
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = tasks.map(task => `
        <tr data-task-id="${task.id}">
            <td><strong>${escapeHtml(task.name)}</strong></td>
            <td>${escapeHtml(task.project_name || '-')}</td>
            <td>${formatDate(task.start_date)}</td>
            <td>${formatDate(task.end_date)}</td>
            <td>${task.duration_days} dias</td>
            <td>${escapeHtml(task.assignee || '-')}</td>
            <td><span class="status-badge ${task.status}">${getStatusLabel(task.status)}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-icon" onclick="openTaskModal(${task.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-icon btn-danger" onclick="confirmDeleteTask(${task.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function openTaskModal(taskId = null) {
    const modal = document.getElementById('taskModal');
    const form = document.getElementById('taskForm');
    const title = document.getElementById('taskModalTitle');
    const projectSelect = document.getElementById('taskProject');

    form.reset();
    document.getElementById('taskId').value = '';

    // Preenche select de projetos
    projectSelect.innerHTML = '<option value="">Selecione um projeto</option>' +
        App.projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');

    if (taskId) {
        title.textContent = 'Editar Tarefa';
        const task = App.tasks.find(t => t.id === taskId);
        if (task) {
            document.getElementById('taskId').value = task.id;
            document.getElementById('taskProject').value = task.project_id;
            document.getElementById('taskName').value = task.name;
            document.getElementById('taskStartDate').value = task.start_date;
            document.getElementById('taskEndDate').value = task.end_date;
            document.getElementById('taskStatus').value = task.status;
            document.getElementById('taskAssignee').value = task.assignee || '';
        }
    } else {
        title.textContent = 'Nova Tarefa';
        // Define datas padrão
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('taskStartDate').value = today;
        document.getElementById('taskEndDate').value = today;
    }

    modal.classList.add('active');
}

async function saveTask(e) {
    e.preventDefault();

    const taskId = document.getElementById('taskId').value;
    const data = {
        project_id: parseInt(document.getElementById('taskProject').value),
        name: document.getElementById('taskName').value,
        start_date: document.getElementById('taskStartDate').value,
        end_date: document.getElementById('taskEndDate').value,
        status: document.getElementById('taskStatus').value,
        assignee: document.getElementById('taskAssignee').value || null
    };

    try {
        if (taskId) {
            await API.updateTask(taskId, data);
            showToast('Tarefa atualizada com sucesso!', 'success');
        } else {
            await API.createTask(data);
            showToast('Tarefa criada com sucesso!', 'success');
        }

        closeModal('taskModal');

        // Recarrega dados baseado na view atual
        if (App.currentView === 'tasks') {
            await loadTasks();
        } else if (App.currentView === 'gantt') {
            await loadGantt();
        }
        await loadDashboard();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function confirmDeleteTask(taskId) {
    const task = App.tasks.find(t => t.id === taskId);
    document.getElementById('confirmMessage').textContent =
        `Tem certeza que deseja excluir a tarefa "${task?.name}"?`;

    App.deleteCallback = async () => {
        try {
            await API.deleteTask(taskId);
            showToast('Tarefa excluída com sucesso!', 'success');
            closeModal('confirmModal');

            if (App.currentView === 'tasks') {
                await loadTasks();
            } else if (App.currentView === 'gantt') {
                await loadGantt();
            }
            await loadDashboard();
        } catch (error) {
            showToast(error.message, 'error');
        }
    };

    document.getElementById('confirmModal').classList.add('active');
}

// ============================================
// Modais
// ============================================
function setupModals() {
    // Fechar modais
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            modal.classList.remove('active');
        });
    });

    // Fechar ao clicar no overlay
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', () => {
            const modal = overlay.closest('.modal');
            modal.classList.remove('active');
        });
    });

    // Confirmar exclusão
    document.getElementById('btnConfirmDelete').addEventListener('click', () => {
        if (App.deleteCallback) {
            App.deleteCallback();
        }
    });
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// ============================================
// Formulários
// ============================================
function setupForms() {
    document.getElementById('projectForm').addEventListener('submit', saveProject);
    document.getElementById('taskForm').addEventListener('submit', saveTask);
}

// ============================================
// Filtros
// ============================================
function setupFilters() {
    // Filtro de projeto no Gantt
    document.getElementById('projectSelect').addEventListener('change', loadGantt);

    // Filtros de tarefas
    document.getElementById('filterProject').addEventListener('change', loadTasks);
    document.getElementById('filterStatus').addEventListener('change', loadTasks);
}

function updateProjectSelects(projects) {
    const selects = ['projectSelect', 'filterProject', 'taskProject'];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return;

        const currentValue = select.value;
        const firstOption = select.querySelector('option:first-child');
        const firstOptionText = firstOption ? firstOption.textContent : 'Selecione';

        select.innerHTML = `<option value="">${firstOptionText}</option>` +
            projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');

        // Mantém valor selecionado se ainda existir
        if (currentValue && projects.some(p => p.id == currentValue)) {
            select.value = currentValue;
        }
    });
}

// ============================================
// Tema
// ============================================
function setupTheme() {
    const toggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('theme') || 'light';

    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        toggle.innerHTML = '<i class="fas fa-sun"></i><span>Modo Claro</span>';
    }

    toggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        toggle.innerHTML = newTheme === 'dark'
            ? '<i class="fas fa-sun"></i><span>Modo Claro</span>'
            : '<i class="fas fa-moon"></i><span>Modo Escuro</span>';
    });
}

// ============================================
// Toast Notifications
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');

    const icons = {
        success: 'fa-check',
        error: 'fa-times',
        warning: 'fa-exclamation',
        info: 'fa-info'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${icons[type]}"></i>
        </div>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto remove após 5 segundos
    const timeout = setTimeout(() => removeToast(toast), 5000);

    // Fechar manualmente
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(timeout);
        removeToast(toast);
    });
}

function removeToast(toast) {
    toast.classList.add('toast-out');
    setTimeout(() => toast.remove(), 300);
}

// ============================================
// Utilitários
// ============================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
}

function getStatusLabel(status) {
    const labels = {
        todo: 'A Fazer',
        doing: 'Fazendo',
        review: 'Revisão',
        done: 'Concluído'
    };
    return labels[status] || status;
}
