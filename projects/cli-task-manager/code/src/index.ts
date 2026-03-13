#!/usr/bin/env node

import { Command } from 'commander';
import { createAddCommand } from './commands/add.js';
import { createListCommand } from './commands/list.js';
import { createCompleteCommand } from './commands/complete.js';
import { createDeleteCommand } from './commands/delete.js';

const program = new Command();

program
  .name('task')
  .description('CLI Task Manager — organize your tasks with style')
  .version('1.0.0');

program.addCommand(createAddCommand());
program.addCommand(createListCommand());
program.addCommand(createCompleteCommand());
program.addCommand(createDeleteCommand());

// Default: show help if no command
program.action(() => {
  program.outputHelp();
});

program.parse();