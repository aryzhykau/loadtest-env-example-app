/**
 * API service for making HTTP requests to the backend
 */
import axios from 'axios';
import {
  API_BASE_URL,
  DataEntry,
  DataEntryCreate,
  DataEntryUpdate,
  TaskCreate,
  TaskResponse,
  HealthCheck,
  Metrics,
} from '../types/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health & Metrics

export const getHealth = async (): Promise<HealthCheck> => {
  const { data } = await api.get<HealthCheck>('/health');
  return data;
};

export const getMetrics = async (): Promise<Metrics> => {
  const { data } = await api.get<Metrics>('/metrics');
  return data;
};

// Tasks

export const createTask = async (task: TaskCreate): Promise<TaskResponse> => {
  const { data } = await api.post<TaskResponse>('/tasks', task);
  return data;
};

export const getTaskStatus = async (taskId: string): Promise<TaskResponse> => {
  const { data } = await api.get<TaskResponse>(`/tasks/${taskId}`);
  return data;
};

// Data Entries

export const listDataEntries = async (
  skip = 0,
  limit = 100
): Promise<DataEntry[]> => {
  const { data } = await api.get<DataEntry[]>('/data', {
    params: { skip, limit },
  });
  return data;
};

export const createDataEntry = async (
  entry: DataEntryCreate
): Promise<DataEntry> => {
  const { data } = await api.post<DataEntry>('/data', entry);
  return data;
};

export const getDataEntry = async (id: string): Promise<DataEntry> => {
  const { data } = await api.get<DataEntry>(`/data/${id}`);
  return data;
};

export const updateDataEntry = async (
  id: string,
  entry: DataEntryUpdate
): Promise<DataEntry> => {
  const { data } = await api.put<DataEntry>(`/data/${id}`, entry);
  return data;
};

export const deleteDataEntry = async (id: string): Promise<void> => {
  await api.delete(`/data/${id}`);
};

export default api;
