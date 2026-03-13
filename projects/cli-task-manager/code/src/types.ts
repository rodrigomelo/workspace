export type Priority = 'low' | 'medium' | 'high';
export type Status = 'pending' | 'completed';

export interface Task {
  id: number;
  text: string;
  priority: Priority;
  status: Status;
  createdAt: string; // ISO date
  completedAt?: string;
}

export interface Config {
  storagePath: string;
}