import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

interface ApiResponse<T = any> {
  data: T;
  message?: string;
  error?: string;
}

interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

interface Project {
  id: string;
  name: string;
  description?: string;
  topic: string;
  status: string;
  priority: string;
  created_by: {
    id: string;
    username: string;
    full_name: string;
  };
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface OrchestrationRun {
  id: string;
  project?: {
    id: string;
    name: string;
  };
  topic: string;
  status: string;
  success_rate: number;
  execution_time_ms: number;
  created_at: string;
}

interface UsageAnalytics {
  api_usage: Array<{
    date: string;
    requests: number;
    tokens: number;
    avg_response_time: number;
  }>;
  runs_summary: {
    total_runs: number;
    completed_runs: number;
    failed_runs: number;
    avg_execution_time: number;
    success_rate: number;
  };
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string): Promise<ApiResponse> {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
    localStorage.removeItem('auth_token');
  }

  async refreshToken(): Promise<ApiResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  // Organizations
  async getCurrentOrganization(): Promise<ApiResponse> {
    const response = await this.client.get('/organizations/current');
    return response.data;
  }

  async updateOrganization(data: Record<string, any>): Promise<ApiResponse> {
    const response = await this.client.put('/organizations/current', data);
    return response.data;
  }

  // Projects
  async listProjects(params?: {
    status?: string;
    priority?: string;
    limit?: number;
    offset?: number;
    search?: string;
  }): Promise<PaginatedResponse<Project>> {
    const response = await this.client.get('/projects', { params });
    return response.data;
  }

  async createProject(data: {
    name: string;
    description?: string;
    topic: string;
    priority?: string;
    metadata?: Record<string, any>;
  }): Promise<ApiResponse> {
    const response = await this.client.post('/projects', data);
    return response.data;
  }

  async getProject(id: string): Promise<Project> {
    const response = await this.client.get(`/projects/${id}`);
    return response.data;
  }

  async updateProject(id: string, data: Partial<Project>): Promise<ApiResponse> {
    const response = await this.client.put(`/projects/${id}`, data);
    return response.data;
  }

  async deleteProject(id: string): Promise<ApiResponse> {
    const response = await this.client.delete(`/projects/${id}`);
    return response.data;
  }

  // Orchestrations
  async startOrchestration(data: {
    project_id?: string;
    topic: string;
    integration_enabled?: boolean;
    custom_phases?: string[];
    template_id?: string;
    settings?: Record<string, any>;
  }): Promise<ApiResponse> {
    const response = await this.client.post('/orchestrate', data);
    return response.data;
  }

  async getOrchestrationStatus(runId: string): Promise<ApiResponse> {
    const response = await this.client.get(`/orchestration/${runId}`);
    return response.data;
  }

  async listOrchestrations(params?: {
    project_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaginatedResponse<OrchestrationRun>> {
    const response = await this.client.get('/orchestration', { params });
    return response.data;
  }

  async cancelOrchestration(runId: string): Promise<ApiResponse> {
    const response = await this.client.post(`/orchestration/${runId}/cancel`);
    return response.data;
  }

  // Templates
  async listTemplates(params?: {
    category?: string;
    is_public?: boolean;
    search?: string;
  }): Promise<ApiResponse> {
    const response = await this.client.get('/templates', { params });
    return response.data;
  }

  async createTemplate(data: {
    name: string;
    description?: string;
    category?: string;
    template_data: Record<string, any>;
    is_public?: boolean;
  }): Promise<ApiResponse> {
    const response = await this.client.post('/templates', data);
    return response.data;
  }

  async getTemplate(id: string): Promise<ApiResponse> {
    const response = await this.client.get(`/templates/${id}`);
    return response.data;
  }

  // Analytics
  async getUsageAnalytics(days: number = 30): Promise<UsageAnalytics> {
    const response = await this.client.get('/analytics/usage', { params: { days } });
    return response.data;
  }

  async getPerformanceAnalytics(): Promise<ApiResponse> {
    const response = await this.client.get('/analytics/performance');
    return response.data;
  }

  // Webhooks
  async listWebhooks(): Promise<ApiResponse> {
    const response = await this.client.get('/webhooks');
    return response.data;
  }

  async createWebhook(data: {
    name: string;
    url: string;
    events: string[];
    secret_key?: string;
  }): Promise<ApiResponse> {
    const response = await this.client.post('/webhooks', data);
    return response.data;
  }

  async updateWebhook(id: string, data: Record<string, any>): Promise<ApiResponse> {
    const response = await this.client.put(`/webhooks/${id}`, data);
    return response.data;
  }

  async deleteWebhook(id: string): Promise<ApiResponse> {
    const response = await this.client.delete(`/webhooks/${id}`);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export type { Project, OrchestrationRun, UsageAnalytics, ApiResponse, PaginatedResponse };