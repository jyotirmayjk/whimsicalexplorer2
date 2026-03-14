import { apiClient, getAuthToken, setAuthToken } from './client';
import { ChildSettings } from '../types/settings';

export type BackendSession = {
  id: number;
  household_id: number;
  device_id: number | null;
  active_mode: ChildSettings['defaultMode'];
  voice_style: ChildSettings['voiceStyle'];
  status: string;
  current_object_name: string | null;
  current_object_category: ChildSettings['allowedCategories'][number] | null;
  started_at: string | null;
  last_activity_at: string | null;
};

type AuthResponse = {
  access_token: string;
  token_type: string;
};

// Auth
export const login = (data: any) => apiClient.post<AuthResponse>('/auth/login', data);
export const ensureLogin = async () => {
  const existingToken = await getAuthToken();
  if (existingToken) {
    return existingToken;
  }
  const auth = await login({ name: 'Mobile Test Family' });
  setAuthToken(auth.access_token);
  return auth.access_token as string;
};

// Settings
export const getSettings = async (): Promise<ChildSettings> => {
  await ensureLogin();
  const data = await apiClient.get<any>('/app/settings/');
  return {
    voiceStyle: data.voice_style,
    defaultMode: data.default_mode,
    allowedCategories: data.allowed_categories,
  };
};
export const updateSettings = async (data: Partial<ChildSettings>): Promise<ChildSettings> => {
  await ensureLogin();
  const payload: Record<string, unknown> = {};
  if (data.voiceStyle) payload.voice_style = data.voiceStyle;
  if (data.defaultMode) payload.default_mode = data.defaultMode;
  if (data.allowedCategories) payload.allowed_categories = data.allowedCategories;

  const updated = await apiClient.patch<any>('/app/settings/', payload);
  return {
    voiceStyle: updated.voice_style,
    defaultMode: updated.default_mode,
    allowedCategories: updated.allowed_categories,
  };
};

// Session
export const getCurrentSession = async () => {
  await ensureLogin();
  return apiClient.get<BackendSession>('/app/session/current');
};
export const startSession = async (data: any) => {
  await ensureLogin();
  return apiClient.post<BackendSession>('/app/session/start', data);
};
export const updateCurrentSession = async (data: Partial<BackendSession>) => {
  await ensureLogin();
  return apiClient.patch<BackendSession>('/app/session/current', data);
};
export const endSession = async () => {
  await ensureLogin();
  return apiClient.post('/app/session/end');
};

// Discoveries
export const getDiscoveries = () => apiClient.get<any[]>('/app/discoveries/');
export const favoriteDiscovery = (id: string) => apiClient.post(`/app/discoveries/${id}/favorite`);
export const replayDiscovery = (id: string) => apiClient.post(`/app/discoveries/${id}/replay`);
