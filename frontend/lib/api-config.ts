/**
 * API Configuration
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

/**
 * Custom API Error class with status code
 */
export class ApiError extends Error {
  status: number;
  code: string;

  constructor(message: string, status: number, code: string = 'UNKNOWN_ERROR') {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

/**
 * Error codes for better error handling
 */
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const;

/**
 * Get error code from HTTP status
 */
function getErrorCode(status: number): string {
  switch (status) {
    case 401:
      return ERROR_CODES.UNAUTHORIZED;
    case 403:
      return ERROR_CODES.FORBIDDEN;
    case 404:
      return ERROR_CODES.NOT_FOUND;
    case 400:
    case 422:
      return ERROR_CODES.VALIDATION_ERROR;
    case 500:
    case 502:
    case 503:
      return ERROR_CODES.SERVER_ERROR;
    default:
      return ERROR_CODES.UNKNOWN_ERROR;
  }
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.code) {
      case ERROR_CODES.NETWORK_ERROR:
        return 'Não foi possível conectar ao servidor. Verifique sua conexão.';
      case ERROR_CODES.UNAUTHORIZED:
        return 'Sessão expirada. Faça login novamente.';
      case ERROR_CODES.FORBIDDEN:
        return 'Você não tem permissão para realizar esta ação.';
      case ERROR_CODES.NOT_FOUND:
        return 'Recurso não encontrado.';
      case ERROR_CODES.VALIDATION_ERROR:
        return error.message || 'Dados inválidos. Verifique os campos.';
      case ERROR_CODES.SERVER_ERROR:
        return 'Erro no servidor. Tente novamente mais tarde.';
      default:
        return error.message || 'Ocorreu um erro inesperado.';
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Ocorreu um erro inesperado.';
}

/**
 * Token refresh state to prevent multiple simultaneous refresh attempts
 */
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null;
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`,
      },
    });

    if (!response.ok) return null;

    const data = await response.json();
    const newToken = data.data?.accessToken;
    if (newToken) {
      localStorage.setItem('accessToken', newToken);
      return newToken;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Generic fetch wrapper with error handling and automatic token refresh
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  _isRetry = false
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('accessToken');
    if (token) {
      (defaultHeaders as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }
  }

  // If body is FormData, remove Content-Type so browser sets it with boundary
  if (options.body instanceof FormData) {
    delete (defaultHeaders as Record<string, string>)['Content-Type'];
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    // Handle 401 - try to refresh token (only once, skip for auth endpoints)
    if (response.status === 401 && !_isRetry && !endpoint.startsWith('/auth/')) {
      // Use a single refresh promise to avoid concurrent refresh calls
      if (!isRefreshing) {
        isRefreshing = true;
        refreshPromise = refreshAccessToken().finally(() => {
          isRefreshing = false;
          refreshPromise = null;
        });
      }

      const newToken = await (refreshPromise || refreshAccessToken());

      if (newToken) {
        // Retry the original request with new token
        return apiFetch<T>(endpoint, options, true);
      }

      // Refresh failed - clear tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      }
    }

    const data = await response.json();

    if (!response.ok) {
      const errorCode = getErrorCode(response.status);
      const errorMessage = data.message || `HTTP error ${response.status}`;
      throw new ApiError(errorMessage, response.status, errorCode);
    }

    return data;
  } catch (error) {
    // Network error (no response from server)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError(
        'Não foi possível conectar ao servidor',
        0,
        ERROR_CODES.NETWORK_ERROR
      );
    }

    // Re-throw ApiError
    if (error instanceof ApiError) {
      throw error;
    }

    // Unknown error
    throw new ApiError(
      error instanceof Error ? error.message : 'Erro desconhecido',
      0,
      ERROR_CODES.UNKNOWN_ERROR
    );
  }
}
