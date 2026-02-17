/**
 * ProjectFlow Gantt - Gantt Chart Component
 * Componente de visualização de gráfico de Gantt
 */

class GanttChart {
    constructor(container, options = {}) {
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        this.options = {
            cellWidth: 40,
            rowHeight: 50,
            headerHeight: 60,
            zoom: 'week', // day, week, month
            onTaskClick: null,
            onTaskEdit: null,
            ...options
        };

        this.tasks = [];
        this.startDate = null;
        this.endDate = null;
        this.totalDays = 0;
    }

    /**
     * Define as tarefas e renderiza o gráfico
     * @param {Array} tasks - Lista de tarefas
     */
    setTasks(tasks) {
        this.tasks = tasks || [];

        if (this.tasks.length === 0) {
            this.container.innerHTML = '<p class="empty-state">Nenhuma tarefa encontrada para exibir no Gantt</p>';
            return;
        }

        this.calculateDateRange();
        this.render();
    }

    /**
     * Calcula o intervalo de datas do gráfico
     */
    calculateDateRange() {
        if (this.tasks.length === 0) return;

        // Encontra a menor data de início e maior data de fim
        let minDate = new Date(this.tasks[0].start_date);
        let maxDate = new Date(this.tasks[0].end_date);

        this.tasks.forEach(task => {
            const start = new Date(task.start_date);
            const end = new Date(task.end_date);
            if (start < minDate) minDate = start;
            if (end > maxDate) maxDate = end;
        });

        // Adiciona margem de dias antes e depois
        const margin = this.options.zoom === 'day' ? 3 : this.options.zoom === 'week' ? 7 : 15;

        this.startDate = new Date(minDate);
        this.startDate.setDate(this.startDate.getDate() - margin);

        this.endDate = new Date(maxDate);
        this.endDate.setDate(this.endDate.getDate() + margin);

        // Calcula total de dias
        this.totalDays = Math.ceil((this.endDate - this.startDate) / (1000 * 60 * 60 * 24)) + 1;
    }

    /**
     * Renderiza o gráfico completo
     */
    render() {
        const wrapper = document.createElement('div');
        wrapper.className = 'gantt-wrapper';

        // Sidebar com nomes das tarefas
        wrapper.appendChild(this.renderSidebar());

        // Timeline com barras
        wrapper.appendChild(this.renderTimeline());

        this.container.innerHTML = '';
        this.container.appendChild(wrapper);

        // Scroll para a linha de hoje
        this.scrollToToday();
    }

    /**
     * Renderiza a sidebar com nomes das tarefas
     */
    renderSidebar() {
        const sidebar = document.createElement('div');
        sidebar.className = 'gantt-sidebar';

        // Header
        const header = document.createElement('div');
        header.className = 'gantt-sidebar-header';
        header.textContent = 'Tarefas';
        sidebar.appendChild(header);

        // Rows
        this.tasks.forEach(task => {
            const row = document.createElement('div');
            row.className = 'gantt-sidebar-row';
            row.dataset.taskId = task.id;
            row.innerHTML = `
                <span class="status-dot" style="background: var(--status-${task.status})"></span>
                <span class="task-name" title="${task.name}">${task.name}</span>
            `;

            row.addEventListener('click', () => {
                if (this.options.onTaskClick) {
                    this.options.onTaskClick(task);
                }
            });

            sidebar.appendChild(row);
        });

        return sidebar;
    }

    /**
     * Renderiza a timeline com as barras
     */
    renderTimeline() {
        const timeline = document.createElement('div');
        timeline.className = 'gantt-timeline';

        // Header com datas
        timeline.appendChild(this.renderHeader());

        // Body com barras das tarefas
        timeline.appendChild(this.renderBody());

        return timeline;
    }

    /**
     * Renderiza o header com as datas
     */
    renderHeader() {
        const header = document.createElement('div');
        header.className = 'gantt-header';
        header.style.width = `${this.totalDays * this.options.cellWidth}px`;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
        const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

        for (let i = 0; i < this.totalDays; i++) {
            const date = new Date(this.startDate);
            date.setDate(date.getDate() + i);

            const cell = document.createElement('div');
            cell.className = 'gantt-header-cell';
            cell.style.minWidth = `${this.options.cellWidth}px`;

            // Marca fins de semana
            if (date.getDay() === 0 || date.getDay() === 6) {
                cell.classList.add('weekend');
            }

            // Marca hoje
            if (date.getTime() === today.getTime()) {
                cell.classList.add('today');
            }

            // Conteúdo baseado no zoom
            if (this.options.zoom === 'day') {
                cell.innerHTML = `
                    <span class="day-name">${dayNames[date.getDay()]}</span>
                    <span class="day-number">${date.getDate()}</span>
                `;
            } else if (this.options.zoom === 'week') {
                if (date.getDay() === 1 || i === 0) { // Segunda ou primeiro dia
                    cell.innerHTML = `
                        <span class="day-name">${monthNames[date.getMonth()]}</span>
                        <span class="day-number">${date.getDate()}</span>
                    `;
                } else {
                    cell.innerHTML = `
                        <span class="day-number">${date.getDate()}</span>
                    `;
                }
            } else { // month
                if (date.getDate() === 1 || i === 0) {
                    cell.innerHTML = `
                        <span class="day-name">${monthNames[date.getMonth()]}</span>
                        <span class="day-number">${date.getFullYear()}</span>
                    `;
                } else if (date.getDate() % 5 === 0) {
                    cell.innerHTML = `<span class="day-number">${date.getDate()}</span>`;
                }
            }

            header.appendChild(cell);
        }

        return header;
    }

    /**
     * Renderiza o body com as barras das tarefas
     */
    renderBody() {
        const body = document.createElement('div');
        body.className = 'gantt-body';
        body.style.width = `${this.totalDays * this.options.cellWidth}px`;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // Renderiza cada linha de tarefa
        this.tasks.forEach(task => {
            const row = document.createElement('div');
            row.className = 'gantt-row';
            row.dataset.taskId = task.id;

            // Células de fundo
            for (let i = 0; i < this.totalDays; i++) {
                const date = new Date(this.startDate);
                date.setDate(date.getDate() + i);

                const cell = document.createElement('div');
                cell.className = 'gantt-cell';
                cell.style.minWidth = `${this.options.cellWidth}px`;

                if (date.getDay() === 0 || date.getDay() === 6) {
                    cell.classList.add('weekend');
                }

                if (date.getTime() === today.getTime()) {
                    cell.classList.add('today');
                }

                row.appendChild(cell);
            }

            // Barra da tarefa
            const bar = this.createTaskBar(task);
            row.appendChild(bar);

            body.appendChild(row);
        });

        // Linha vertical de hoje
        const todayIndex = this.getDayIndex(today);
        if (todayIndex >= 0 && todayIndex < this.totalDays) {
            const todayLine = document.createElement('div');
            todayLine.className = 'gantt-today-line';
            todayLine.style.left = `${todayIndex * this.options.cellWidth + this.options.cellWidth / 2}px`;
            body.appendChild(todayLine);
        }

        return body;
    }

    /**
     * Cria a barra visual de uma tarefa
     * @param {Object} task - Dados da tarefa
     */
    createTaskBar(task) {
        const startDate = new Date(task.start_date);
        const endDate = new Date(task.end_date);

        const startIndex = this.getDayIndex(startDate);
        const endIndex = this.getDayIndex(endDate);
        const duration = endIndex - startIndex + 1;

        const bar = document.createElement('div');
        bar.className = `gantt-bar ${task.status}`;
        bar.style.left = `${startIndex * this.options.cellWidth}px`;
        bar.style.width = `${duration * this.options.cellWidth - 4}px`;
        bar.dataset.taskId = task.id;

        // Tooltip com informações
        bar.title = `${task.name}
Início: ${this.formatDate(startDate)}
Fim: ${this.formatDate(endDate)}
Duração: ${task.duration_days} dias
Status: ${this.getStatusLabel(task.status)}
${task.assignee ? 'Responsável: ' + task.assignee : ''}`;

        // Texto da barra (se couber)
        if (duration >= 3) {
            bar.textContent = task.name;
        }

        // Event listeners
        bar.addEventListener('click', (e) => {
            e.stopPropagation();
            if (this.options.onTaskClick) {
                this.options.onTaskClick(task);
            }
        });

        bar.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            if (this.options.onTaskEdit) {
                this.options.onTaskEdit(task);
            }
        });

        return bar;
    }

    /**
     * Calcula o índice do dia no gráfico
     * @param {Date} date - Data
     */
    getDayIndex(date) {
        const d = new Date(date);
        d.setHours(0, 0, 0, 0);
        const start = new Date(this.startDate);
        start.setHours(0, 0, 0, 0);
        return Math.floor((d - start) / (1000 * 60 * 60 * 24));
    }

    /**
     * Formata data para exibição
     * @param {Date} date - Data
     */
    formatDate(date) {
        return date.toLocaleDateString('pt-BR');
    }

    /**
     * Retorna label do status
     * @param {string} status - Status
     */
    getStatusLabel(status) {
        const labels = {
            todo: 'A Fazer',
            doing: 'Fazendo',
            review: 'Em Revisão',
            done: 'Concluído'
        };
        return labels[status] || status;
    }

    /**
     * Faz scroll até a linha de hoje
     */
    scrollToToday() {
        const today = new Date();
        const todayIndex = this.getDayIndex(today);

        if (todayIndex >= 0 && todayIndex < this.totalDays) {
            const timeline = this.container.querySelector('.gantt-timeline');
            if (timeline) {
                const scrollPosition = Math.max(0, todayIndex * this.options.cellWidth - timeline.clientWidth / 2);
                timeline.scrollLeft = scrollPosition;
            }
        }
    }

    /**
     * Define o nível de zoom
     * @param {string} zoom - Nível de zoom (day, week, month)
     */
    setZoom(zoom) {
        this.options.zoom = zoom;

        // Ajusta largura das células baseado no zoom
        switch (zoom) {
            case 'day':
                this.options.cellWidth = 60;
                break;
            case 'week':
                this.options.cellWidth = 40;
                break;
            case 'month':
                this.options.cellWidth = 20;
                break;
        }

        if (this.tasks.length > 0) {
            this.calculateDateRange();
            this.render();
        }
    }

    /**
     * Atualiza uma tarefa específica
     * @param {Object} updatedTask - Tarefa atualizada
     */
    updateTask(updatedTask) {
        const index = this.tasks.findIndex(t => t.id === updatedTask.id);
        if (index !== -1) {
            this.tasks[index] = updatedTask;
            this.calculateDateRange();
            this.render();
        }
    }

    /**
     * Remove uma tarefa
     * @param {number} taskId - ID da tarefa
     */
    removeTask(taskId) {
        this.tasks = this.tasks.filter(t => t.id !== taskId);
        if (this.tasks.length > 0) {
            this.calculateDateRange();
            this.render();
        } else {
            this.container.innerHTML = '<p class="empty-state">Nenhuma tarefa encontrada para exibir no Gantt</p>';
        }
    }

    /**
     * Adiciona uma nova tarefa
     * @param {Object} task - Nova tarefa
     */
    addTask(task) {
        this.tasks.push(task);
        this.calculateDateRange();
        this.render();
    }
}

// Exporta para uso global
window.GanttChart = GanttChart;
