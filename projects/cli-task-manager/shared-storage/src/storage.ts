import { homedir } from 'os';
import { join, dirname } from 'path';
import { promises as fs } from 'fs';

export type Priority = 'low' | 'medium' | 'high';
export type Status = 'pending' | 'completed';

export interface Task {
  id: number;
  text: string;
  priority: Priority;
  status: Status;
  createdAt: string;
  completedAt?: string;
}

const STORAGE_PATH = getStoragePath();
const COUNTER_PATH = getCounterPath();

function getStoragePath(): string {
  return join(homedir(), '.config', 'clawlab', 'tasks.json');
}

function getCounterPath(): string {
  return join(homedir(), '.config', 'clawlab', 'counter.json');
}

async function ensureDir(): Promise<void> {
  const dir = dirname(STORAGE_PATH);
  try {
    await fs.access(dir);
  } catch {
    await fs.mkdir(dir, { recursive: true });
  }
}

export async function loadCounter(): Promise<number> {
  try {
    const data = await fs.readFile(COUNTER_PATH, 'utf-8');
    const parsed = JSON.parse(data);
    return typeof parsed.nextId === 'number' ? parsed.nextId : 1;
  } catch {
    return 1;
  }
}

export async function saveCounter(nextId: number): Promise<void> {
  await ensureDir();
  await fs.writeFile(COUNTER_PATH, JSON.stringify({ nextId }), 'utf-8');
}

export async function loadTasks(): Promise<Task[]> {
  try {
    await ensureDir();
    const data = await fs.readFile(STORAGE_PATH, 'utf-8');
    return JSON.parse(data) as Task[];
  } catch (err: unknown) {
    if ((err as any).code === 'ENOENT') return [];
    if (err instanceof SyntaxError) return [];
    throw err;
  }
}

export async function saveTasks(tasks: Task[]): Promise<void> {
  await ensureDir();
  await fs.writeFile(STORAGE_PATH, JSON.stringify(tasks, null, 2), 'utf-8');
}

export async function addTask(text: string, priority: Priority = 'medium'): Promise<Task> {
  const tasks = await loadTasks();
  const nextId = await loadCounter();
  const newTask: Task = {
    id: nextId,
    text,
    priority,
    status: 'pending',
    createdAt: new Date().toISOString(),
  };
  tasks.push(newTask);
  await saveTasks(tasks);
  await saveCounter(nextId + 1);
  return newTask;
}

export async function completeTask(id: number): Promise<Task | null> {
  const tasks = await loadTasks();
  const task = tasks.find(t => t.id === id);
  if (!task) return null;
  task.status = 'completed';
  task.completedAt = new Date().toISOString();
  await saveTasks(tasks);
  return task;
}

export async function deleteTask(id: number): Promise<boolean> {
  const tasks = await loadTasks();
  const index = tasks.findIndex(t => t.id === id);
  if (index === -1) return false;
  tasks.splice(index, 1);
  await saveTasks(tasks);
  return true;
}