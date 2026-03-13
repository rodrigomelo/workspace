const API_BASE = 'http://localhost:3000/api';

let tasks = [];
let currentFilter = { status: 'all', priority: 'all' };
let deleteTargetId = null;

// DOM elements
const taskList = document.getElementById('taskList');
const addBtn = document.getElementById('addBtn');
const addModal = document.getElementById('addModal');
const cancelBtn = document.getElementById('cancelBtn');
const confirmAddBtn = document.getElementById('confirmAddBtn');
const taskText = document.getElementById('taskText');
const taskPriority = document.getElementById('taskPriority');
const deleteModal = document.getElementById('deleteModal');
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
const deleteTaskId = document.getElementById('deleteTaskId');
const toast = document.getElementById('toast');
const filterBtns = document.querySelectorAll('.filter-btn');
const priorityFilter = document.getElementById('priorityFilter');

// Fetch tasks
async function loadTasks() {
  try {
    const res = await fetch(`${API_BASE}/tasks`);
    tasks = await res.json();
    renderTasks();
  } catch (err) {
    showToast('Failed to load tasks', 'error');
  }
}

// Render task list
function renderTasks() {
  let filtered = tasks;

  if (currentFilter.status !== 'all') {
    filtered = filtered.filter(t => t.status === currentFilter.status);
  }
  if (currentFilter.priority !== 'all') {
    filtered = filtered.filter(t => t.priority === currentFilter.priority);
  }

  // Sort: pending first, then by id desc
  filtered.sort((a, b) => {
    if (a.status !== b.status) return a.status === 'pending' ? -1 : 1;
    return b.id - a.id;
  });

  if (filtered.length === 0) {
    taskList.innerHTML = '<div class="empty">📋 No tasks match your criteria.</div>';
    return;
  }

  taskList.innerHTML = filtered.map(task => `
    <div class="task-card ${task.status}">
      <div class="task-indicator ${task.priority}"></div>
      <div class="task-content">
        <div class="task-id">ID: ${task.id}</div>
        <div class="task-text">${escapeHtml(task.text)}</div>
      </div>
      <div class="task-actions">
        <input type="checkbox" class="checkbox" ${task.status === 'completed' ? 'checked' : ''} 
          onchange="toggleComplete(${task.id})">
        <button class="icon-btn" onclick="confirmDelete(${task.id})">🗑️</button>
      </div>
    </div>
  `).join('');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Add task
async function addTask() {
  const text = taskText.value.trim();
  const priority = taskPriority.value;
  if (!text) return;

  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, priority })
    });
    if (!res.ok) throw new Error('Failed');
    hideAddModal();
    taskText.value = '';
    showToast('Task added!', 'success');
    await loadTasks();
  } catch (err) {
    showToast('Failed to add task', 'error');
  }
}

// Toggle complete
async function toggleComplete(id) {
  try {
    const res = await fetch(`${API_BASE}/tasks/${id}/complete`, { method: 'PATCH' });
    if (!res.ok) throw new Error('Failed');
    showToast('Task completed!', 'success');
    await loadTasks();
  } catch (err) {
    showToast('Failed to complete task', 'error');
  }
}

// Delete task
function confirmDelete(id) {
  deleteTargetId = id;
  deleteTaskId.textContent = `#${id}`;
  deleteModal.classList.remove('hidden');
}

async function deleteTask() {
  if (!deleteTargetId) return;
  try {
    const res = await fetch(`${API_BASE}/tasks/${deleteTargetId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed');
    hideDeleteModal();
    showToast('Task deleted!', 'success');
    await loadTasks();
  } catch (err) {
    showToast('Failed to delete task', 'error');
  }
}

function hideAddModal() { addModal.classList.add('hidden'); }
function showAddModal() { addModal.classList.remove('hidden'); taskText.focus(); }
function hideDeleteModal() { deleteModal.classList.add('hidden'); deleteTargetId = null; }

function showToast(msg, type = 'success') {
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  setTimeout(() => toast.classList.add('hidden'), 3000);
}

// Event listeners
addBtn.addEventListener('click', showAddModal);
cancelBtn.addEventListener('click', hideAddModal);
confirmAddBtn.addEventListener('click', addTask);
cancelDeleteBtn.addEventListener('click', hideDeleteModal);
confirmDeleteBtn.addEventListener('click', deleteTask);

addModal.addEventListener('click', (e) => {
  if (e.target === addModal) hideAddModal();
});
deleteModal.addEventListener('click', (e) => {
  if (e.target === deleteModal) hideDeleteModal();
});

taskText.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') addTask();
});

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter.status = btn.dataset.status;
    renderTasks();
  });
});

priorityFilter.addEventListener('change', () => {
  currentFilter.priority = priorityFilter.value;
  renderTasks();
});

// Auto-refresh every 5 seconds
setInterval(loadTasks, 5000);

// Init
loadTasks();