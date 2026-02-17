/**
 * ProjectFlow Gantt - API Service
 * Comunicação com o backend Flask
 */

const API = {
    // Base URL da API
    baseUrl: 'http://localhost:5000/api',

    /**
     * Realiza requisição HTTP para a API
     * @param {string} endpoint - Endpoint da API
     * @param {object} options - Opções do fetch
     * @returns {Promise} - Resposta da API
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                throw new Error('Não foi possível conectar ao servidor. Verifique se o backend está rodando.');
            }
            throw error;
        }
    },

    // ==================== PROJECTS ====================

    /**
     * Lista todos os projetos
     * @returns {Promise<Array>} Lista de projetos
     */
    async getProjects() {
        const response = await this.request('/projects');
        return response.data;
    },

    /**
     * Obtém um projeto pelo ID
     * @param {number} id - ID do projeto
     * @returns {Promise<Object>} Dados do projeto
     */
    async getProject(id) {
        const response = await this.request(`/projects/${id}`);
        return response.data;
    },

    /**
     * Cria um novo projeto
     * @param {Object} data - Dados do projeto {name, description}
     * @returns {Promise<Object>} Projeto criado
     */
    async createProject(data) {
        const response = await this.request('/projects', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return response.data;
    },

    /**
     * Atualiza um projeto
     * @param {number} id - ID do projeto
     * @param {Object} data - Dados a atualizar
     * @returns {Promise<Object>} Projeto atualizado
     */
    async updateProject(id, data) {
        const response = await this.request(`/projects/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
        return response.data;
    },

    /**
     * Deleta um projeto
     * @param {number} id - ID do projeto
     * @returns {Promise<boolean>} Sucesso
     */
    async deleteProject(id) {
        await this.request(`/projects/${id}`, {
            method: 'DELETE',
        });
        return true;
    },

    /**
     * Lista tarefas de um projeto
     * @param {number} projectId - ID do projeto
     * @returns {Promise<Array>} Lista de tarefas
     */
    async getProjectTasks(projectId) {
        const response = await this.request(`/projects/${projectId}/tasks`);
        return response.data;
    },

    // ==================== TASKS ====================

    /**
     * Lista todas as tarefas
     * @returns {Promise<Array>} Lista de tarefas
     */
    async getTasks() {
        const response = await this.request('/tasks');
        return response.data;
    },

    /**
     * Obtém uma tarefa pelo ID
     * @param {number} id - ID da tarefa
     * @returns {Promise<Object>} Dados da tarefa
     */
    async getTask(id) {
        const response = await this.request(`/tasks/${id}`);
        return response.data;
    },

    /**
     * Cria uma nova tarefa
     * @param {Object} data - Dados da tarefa
     * @returns {Promise<Object>} Tarefa criada
     */
    async createTask(data) {
        const response = await this.request('/tasks', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return response.data;
    },

    /**
     * Atualiza uma tarefa
     * @param {number} id - ID da tarefa
     * @param {Object} data - Dados a atualizar
     * @returns {Promise<Object>} Tarefa atualizada
     */
    async updateTask(id, data) {
        const response = await this.request(`/tasks/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
        return response.data;
    },

    /**
     * Deleta uma tarefa
     * @param {number} id - ID da tarefa
     * @returns {Promise<boolean>} Sucesso
     */
    async deleteTask(id) {
        await this.request(`/tasks/${id}`, {
            method: 'DELETE',
        });
        return true;
    },

    // ==================== DASHBOARD ====================

    /**
     * Obtém métricas do dashboard
     * @returns {Promise<Object>} Métricas
     */
    async getDashboard() {
        const response = await this.request('/dashboard');
        return response.data;
    },
};

// Exporta para uso global
window.API = API;
