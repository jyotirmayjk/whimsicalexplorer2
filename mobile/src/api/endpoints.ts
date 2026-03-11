import { apiClient } from './client';
import { ChildSettings } from '../types/settings';

// Auth
export const login = (data: any) => apiClient.post('/auth/login', data);

// Settings
export const getSettings = () => apiClient.get<ChildSettings>('/app/settings');
export const updateSettings = (data: Partial<ChildSettings>) => apiClient.patch<ChildSettings>('/app/settings', data);

// Session
export const getCurrentSession = () => apiClient.get('/app/session/current');
export const startSession = (data: any) => apiClient.post('/app/session/start', data);
export const endSession = () => apiClient.post('/app/session/end');

// Discoveries
export const getDiscoveries = () => apiClient.get<any[]>('/app/discoveries');
export const favoriteDiscovery = (id: string) => apiClient.post(`/app/discoveries/${id}/favorite`);
export const replayDiscovery = (id: string) => apiClient.post(`/app/discoveries/${id}/replay`);
