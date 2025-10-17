/**
 * API configuration and types
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface DataEntry {
  _id: string;
  name: string;
  description?: string;
  value: number;
  status: 'active' | 'inactive' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface DataEntryCreate {
  name: string;
  description?: string;
  value: number;
  status?: 'active' | 'inactive' | 'archived';
}

export interface DataEntryUpdate {
  name?: string;
  description?: string;
  value?: number;
  status?: 'active' | 'inactive' | 'archived';
}

export interface TaskCreate {
  task_type: string;
  params?: Record<string, any>;
}

export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'started' | 'progress' | 'success' | 'failure' | 'retry';
  task_type: string;
  created_at: string;
  result?: any;
  error?: string;
}

export interface HealthCheck {
  status: string;
  mongodb: string;
  redis: string;
  celery: string;
}

export interface Metrics {
  total_tasks: number;
  active_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  total_data_entries: number;
}
