import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { Task } from '../types.js';

const CONFIG_DIR = join(homedir(), '.config', 'clawlab');
const STORAGE_FILE = join(CONFIG_DIR, 'tasks.json');
const COUNTER_FILE = join(CONFIG_DIR, 'counter.json');

export async function ensureStorageDir(): Promise<void> {
  if (!existsSync(CONFIG_DIR)) {
    await mkdir(CONFIG_DIR, { recursive: true });
  }
}

export async function loadCounter(): Promise<number> {
  try {
    const data = await readFile(COUNTER_FILE, 'utf-8');
    const parsed = JSON.parse(data);
    return typeof parsed.nextId === 'number' ? parsed.nextId : 1;
  } catch {
    return 1; // default start
  }
}

export async function saveCounter(nextId: number): Promise<void> {
  await ensureStorageDir();
  await writeFile(COUNTER_FILE, JSON.stringify({ nextId }), 'utf-8');
}

export async function loadTasks(): Promise<Task[]> {
  try {
    await ensureStorageDir();
    const data = await readFile(STORAGE_FILE, 'utf-8');
    return JSON.parse(data) as Task[];
  } catch (err: unknown) {
    // If file doesn't exist, return empty array
    if (err instanceof Error && (err as any).code === 'ENOENT') return [];
    if (err instanceof SyntaxError) return [];
    throw err;
  }
}

export async function saveTasks(tasks: Task[]): Promise<void> {
  await ensureStorageDir();
  await writeFile(STORAGE_FILE, JSON.stringify(tasks, null, 2), 'utf-8');
}

export async function addTask(text: string, priority: 'low' | 'medium' | 'high' = 'medium'): Promise<Task> {
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