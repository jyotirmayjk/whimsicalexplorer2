// src/api/client.ts
const BASE_URL = 'http://localhost:8000/api/v1'; // Defaulting to local dev, will parameterize on build

export const getAuthToken = async (): Promise<string | null> => {
  // TODO: Use SecureStore or AsyncStorage to retrieve JWT
  return null;
};

const request = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const token = await getAuthToken();
  const headers = new Headers(options.headers || {});
  
  headers.append('Content-Type', 'application/json');
  if (token) {
    headers.append('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'API Request Failed');
  }

  const json = await response.json();
  return json.data as T; // Adhering to API Convention `{ data: {} }` spec
};

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, data?: any, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'POST', body: JSON.stringify(data) }),
  patch: <T>(endpoint: string, data?: any, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(data) }),
  delete: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'DELETE' }),
};
