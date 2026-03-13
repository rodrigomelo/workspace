import { Command } from 'commander';
import { deleteTask } from '../lib/storage.js';
import { success, error } from '../lib/ui.js';

export function createDeleteCommand(): Command {
  return new Command('delete')
    .argument('<id>', 'Task ID to delete')
    .action(async (idStr) => {
      const id = parseInt(idStr, 10);
      if (isNaN(id)) {
        console.error(error('Invalid task ID'));
        process.exit(1);
      }

      const deleted = await deleteTask(id);
      if (!deleted) {
        const tasks = await import('../lib/storage.js').then(m => m.loadTasks());
        const allIds = tasks.map(t => t.id);
        console.log(error('Task not found'));
        if (allIds.length > 0) {
          console.log(`Existing IDs: ${allIds.join(', ')}`);
        }
        return;
      }

      console.log(success(`Task #${id} deleted!`));
    });
}