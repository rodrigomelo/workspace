import { Command } from 'commander';
import { completeTask } from '../lib/storage.js';
import { success, error } from '../lib/ui.js';

export function createCompleteCommand(): Command {
  return new Command('complete')
    .argument('<id>', 'Task ID to complete')
    .action(async (idStr) => {
      const id = parseInt(idStr, 10);
      if (isNaN(id)) {
        console.error(error('Invalid task ID'));
        process.exit(1);
      }

      const task = await completeTask(id);
      if (!task) {
        const tasks = await import('../lib/storage.js').then(m => m.loadTasks());
        const availableIds = tasks.filter(t => t.status === 'pending').map(t => t.id);
        console.log(error('Task not found or already completed'));
        if (availableIds.length > 0) {
          console.log(`Available pending IDs: ${availableIds.join(', ')}`);
        } else {
          console.log('No pending tasks.');
        }
        return;
      }

      console.log(success(`Task #${id} completed!`));
    });
}