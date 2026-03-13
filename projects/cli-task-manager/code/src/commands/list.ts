import { Command } from 'commander';
import { loadTasks } from '../lib/storage.js';
import { formatTask, header } from '../lib/ui.js';

export function createListCommand(): Command {
  return new Command('list')
    .option('-s, --status <status>', 'Filter by status: pending|completed')
    .option('-p, --priority <level>', 'Filter by priority: low|medium|high')
    .action(async (options) => {
      let tasks = await loadTasks();

      if (options.status) {
        tasks = tasks.filter(t => t.status === options.status);
      }
      if (options.priority) {
        tasks = tasks.filter(t => t.priority === options.priority);
      }

      const pendingCount = tasks.filter(t => t.status === 'pending').length;
      const completedCount = tasks.filter(t => t.status === 'completed').length;

      console.log(header(`Your Tasks (${pendingCount} pending, ${completedCount} completed)`));
      console.log('');

      if (tasks.length === 0) {
        console.log('📭 No tasks match your criteria.');
        return;
      }

      // Sort: pending first, then by id desc (newest first)
      tasks.sort((a, b) => {
        if (a.status !== b.status) {
          return a.status === 'pending' ? -1 : 1;
        }
        return b.id - a.id;
      });

      for (const task of tasks) {
        console.log(formatTask(task));
      }

      console.log('');
      console.log('💡 Run "task complete <id>" to finish a task');
    });
}