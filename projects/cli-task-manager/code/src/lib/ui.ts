// ANSI color codes (matching spec)
export const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',      // High priority
  yellow: '\x1b[33m',   // Medium priority
  green: '\x1b[32m',    // Low priority
  cyan: '\x1b[36m',     // Headers
  bright: '\x1b[1m',    // IDs
};

export function priorityColor(priority: 'low' | 'medium' | 'high'): string {
  switch (priority) {
    case 'high': return colors.red;
    case 'medium': return colors.yellow;
    case 'low': return colors.green;
  }
}

export function priorityEmoji(priority: 'low' | 'medium' | 'high'): string {
  switch (priority) {
    case 'high': return '🔴';
    case 'medium': return '🟡';
    case 'low': return '🟢';
  }
}

export function formatTask(task: { id: number; text: string; priority: string; status: string }): string {
  const color = priorityColor(task.priority as any);
  const emoji = priorityEmoji(task.priority as any);
  const statusIcon = task.status === 'completed' ? '✅' : '⬜';
  return `${color}${emoji} ${colors.bright}[${task.id}]${colors.reset} ${task.text} ${statusIcon}`;
}

export function header(text: string): string {
  return `${colors.cyan}📋 ${text}${colors.reset}`;
}

export function success(text: string): string {
  return `✅ ${text}${colors.reset}`;
}

export function error(text: string): string {
  return `❌ ${text}${colors.reset}`;
}