import { Command } from 'commander';
import { addTask } from '../lib/storage.js';
import { success, header } from '../lib/ui.js';

export function createAddCommand(): Command {
  return new Command('add')
    .argument('<text>', 'Task description')
    .option('-p, --priority <level>', 'Priority: low, medium, high', 'medium')
    .action(async (text, options) => {
      const priority = options.priority.toLowerCase() as 'low' | 'medium' | 'high';
      if (!['low', 'medium', 'high'].includes(priority)) {
        console.error(`❌ Invalid priority. Use: low, medium, high`);
        process.exit(1);
      }
      const task = await addTask(text, priority);
      console.log(success(`Task #${task.id} added with ${priority} priority!`));
    });
}