import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import cors from 'cors';
import { loadTasks, saveTasks, addTask, completeTask, deleteTask } from '../shared-storage/dist/storage.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(join(__dirname, 'public')));

// API routes
app.get('/api/tasks', async (req, res) => {
  try {
    const tasks = await loadTasks();
    res.json(tasks);
  } catch (err) {
    res.status(500).json({ error: 'Failed to read tasks' });
  }
});

app.post('/api/tasks', async (req, res) => {
  try {
    const { text, priority } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'Text required' });
    }
    const task = await addTask(text, priority || 'medium');
    res.status(201).json(task);
  } catch (err) {
    res.status(500).json({ error: 'Failed to add task' });
  }
});

app.patch('/api/tasks/:id/complete', async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    const task = await completeTask(id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.json(task);
  } catch (err) {
    res.status(500).json({ error: 'Failed to complete task' });
  }
});

app.delete('/api/tasks/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    const deleted = await deleteTask(id);
    if (!deleted) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete task' });
  }
});

app.listen(PORT, () => {
  console.log(`🗂️ CLI Task Manager Web UI running at http://localhost:${PORT}`);
});