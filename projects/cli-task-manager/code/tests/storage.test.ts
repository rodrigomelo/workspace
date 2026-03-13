import { describe, it, expect, beforeEach } from 'vitest';
import { addTask, loadTasks, completeTask, deleteTask } from '../src/lib/storage.js';

// Mock file system? For now, we'll use a temp dir via process.env
beforeEach(async () => {
  // Clean up: delete test file if exists
  const { existsSync, unlinkSync } = await import('fs');
  const { join } = await import('path');
  const { homedir } = await import('os');
  const testPath = join(homedir(), '.config', 'clawlab', 'tasks.json');
  if (existsSync(testPath)) {
    unlinkSync(testPath);
  }
});

describe('Task Storage', () => {
  it('should add a task with default medium priority', async () => {
    const task = await addTask('Test task');
    expect(task.text).toBe('Test task');
    expect(task.priority).toBe('medium');
    expect(task.status).toBe('pending');
    expect(task.id).toBe(1);
  });

  it('should add task with custom priority', async () => {
    const task = await addTask('High priority', 'high');
    expect(task.priority).toBe('high');
  });

  it('should list tasks', async () => {
    await addTask('Task 1');
    await addTask('Task 2');
    const tasks = await loadTasks();
    expect(tasks.length).toBe(2);
  });

  it('should complete a task', async () => {
    const task = await addTask('Complete me');
    expect(task.status).toBe('pending');

    const completed = await completeTask(task.id);
    expect(completed?.status).toBe('completed');
    expect(completed?.completedAt).toBeDefined();
  });

  it('should delete a task', async () => {
    const task = await addTask('Delete me');
    const deleted = await deleteTask(task.id);
    expect(deleted).toBe(true);

    const tasks = await loadTasks();
    expect(tasks.find(t => t.id === task.id)).toBeUndefined();
  });
});