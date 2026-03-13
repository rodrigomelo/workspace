import chalk from 'chalk';

export function formatTask(task: { id: number; text: string; priority: 'low' | 'medium' | 'high' }): string {
  const emoji = priorityEmoji(task.priority);
  const color = priorityChalk(task.priority);
  return `${color}${emoji} ${chalk.bold(`[${task.id}]`)}${chalk.reset} ${task.text}`;
}

export function priorityChalk(priority: 'low' | 'medium' | 'high') {
  switch (priority) {
    case 'high': return chalk.red;
    case 'medium': return chalk.yellow;
    case 'low': return chalk.green;
  }
}

export function priorityEmoji(priority: 'low' | 'medium' | 'high'): string {
  switch (priority) {
    case 'high': return '🔴';
    case 'medium': return '🟡';
    case 'low': return '🟢';
  }
}

export function header(text: string): string {
  return chalk.cyan(`📋 ${text}`);
}

export function success(text: string): string {
  return chalk.green(`✅ ${text}`);
}

export function error(text: string): string {
  return chalk.red(`❌ ${text}`);
}