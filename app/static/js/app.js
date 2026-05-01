// Drag and Drop functionality
let draggedTask = null;

function initDragAndDrop() {
    document.querySelectorAll('.task-card').forEach(card => {
        card.setAttribute('draggable', 'true');
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });

    document.querySelectorAll('.column-tasks').forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragenter', handleDragEnter);
        column.addEventListener('dragleave', handleDragLeave);
    });
}

function getBoardUrl() {
    return currentProjectId ? `/htmx/board?project_id=${currentProjectId}` : '/htmx/board';
}

function handleDragStart(e) {
    draggedTask = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', e.target.dataset.taskId);
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    document.querySelectorAll('.column-tasks').forEach(col => {
        col.style.backgroundColor = '';
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '#dbeafe';
}

function handleDragLeave(e) {
    e.currentTarget.style.backgroundColor = '';
}

async function handleDrop(e) {
    e.preventDefault();
    const columnEl = e.currentTarget.closest('.column');
    const columnId = columnEl.dataset.columnId;
    e.currentTarget.style.backgroundColor = '';

    if (draggedTask) {
        const taskId = draggedTask.dataset.taskId;

        try {
            const response = await fetch(`/api/tasks/${taskId}/move?column_id=${columnId}&order_index=0`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                htmx.ajax('GET', getBoardUrl(), {
                    target: '#board-container',
                    swap: 'innerHTML'
                });
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

// Chat Panel Toggle
function toggleChat() {
    const chatPanel = document.getElementById('chat-panel');
    chatPanel.classList.toggle('hidden');
}

// Send Chat Message
async function sendMessage(event) {
    if (event && event.key && event.key !== 'Enter') return;
    if (event && event.shiftKey) return;

    event.preventDefault();

    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    input.disabled = true;

    // Add user message to chat
    addMessageToChat('user', message);

    try {
        const response = await fetch('/api/agent/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        if (response.ok) {
            const data = await response.json();
            addMessageToChat('assistant', data.message);

            // Refresh board if actions were executed
            if (data.actions && data.actions.length > 0) {
                htmx.ajax('GET', getBoardUrl(), { target: '#board-container', swap: 'innerHTML' });
            }
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('assistant', 'エラーが発生しました。もう一度お試しください。');
    } finally {
        input.disabled = false;
        input.focus();
    }
}

function addMessageToChat(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.textContent = content;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Task Modal
function openTaskModal(taskId = null, columnId = null) {
    const modal = document.getElementById('task-modal');
    const form = document.getElementById('task-form');

    // Reset tabs
    switchTab('basic');

    if (taskId) {
        // Edit mode - fetch task data
        fetch(`/api/tasks/${taskId}`)
            .then(res => res.json())
            .then(task => {
                form.querySelector('[name="task_id"]').value = task.id;
                form.querySelector('[name="project_id"]').value = task.project_id || '';
                form.querySelector('[name="title"]').value = task.title;
                form.querySelector('[name="description"]').value = task.description || '';
                form.querySelector('[name="column_id"]').value = task.column_id;
                form.querySelector('[name="priority"]').value = task.priority;
                form.querySelector('[name="due_date"]').value = task.due_date || '';
                loadTaskSchedules(task.id);
            });
    } else {
        // Create mode
        form.reset();
        form.querySelector('[name="task_id"]').value = '';
        form.querySelector('[name="project_id"]').value = currentProjectId || '';
        if (columnId) {
            form.querySelector('[name="column_id"]').value = columnId;
        }
        document.getElementById('schedule-list').innerHTML = '';
    }

    modal.style.display = 'flex';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}

async function saveTask(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const taskId = formData.get('task_id');

    const data = {
        title: formData.get('title'),
        description: formData.get('description'),
        column_id: parseInt(formData.get('column_id')),
        project_id: parseInt(formData.get('project_id')) || null,
        priority: formData.get('priority'),
        due_date: formData.get('due_date') || null
    };

    try {
        const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
        const method = taskId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeTaskModal();
            htmx.ajax('GET', getBoardUrl(), { target: '#board-container', swap: 'innerHTML' });
        }
    } catch (error) {
        console.error('Error saving task:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('このタスクを削除してもよろしいですか？')) return;

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            htmx.ajax('GET', getBoardUrl(), { target: '#board-container', swap: 'innerHTML' });
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
}

// Schedule management
let currentScheduleResources = [];
let editingTaskId = null;

function openScheduleModalForTask(taskId) {
    editingTaskId = taskId;
    openTaskModal(taskId);
    switchTab('schedule');
}

async function loadTaskSchedules(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/schedules`);
        if (response.ok) {
            const schedules = await response.json();
            renderScheduleList(schedules);
        }
    } catch (error) {
        console.error('Error loading schedules:', error);
    }
}

function renderScheduleList(schedules) {
    const container = document.getElementById('schedule-list');
    if (schedules.length === 0) {
        container.innerHTML = '<p class="empty-schedule">定期実行設定はありません</p>';
        return;
    }

    container.innerHTML = schedules.map(s => `
        <div class="schedule-item">
            <div class="schedule-header">
                <span class="schedule-name">${s.name}</span>
                <span class="schedule-type-badge ${s.command_type}">${s.command_type}</span>
                <span class="schedule-status ${s.is_enabled ? 'enabled' : 'disabled'}">${s.is_enabled ? '有効' : '無効'}</span>
            </div>
            <div class="schedule-detail">${s.command}</div>
            <div class="schedule-actions">
                <button onclick="editSchedule(${s.id})">編集</button>
                <button onclick="runScheduleNow(${s.id})">今すぐ実行</button>
                <button onclick="deleteSchedule(${s.id})">削除</button>
            </div>
        </div>
    `).join('');
}

function openScheduleForm(scheduleId = null) {
    const modal = document.getElementById('schedule-modal');
    const form = document.getElementById('schedule-form');
    form.reset();
    currentScheduleResources = [];
    renderResourceList();

    document.querySelector('[name="task_id_for_schedule"]').value = editingTaskId || '';

    if (scheduleId) {
        fetch(`/api/schedules/${scheduleId}`)
            .then(res => res.json())
            .then(schedule => {
                form.querySelector('[name="schedule_id"]').value = schedule.id;
                form.querySelector('[name="schedule_name"]').value = schedule.name;
                form.querySelector('[name="command_type"]').value = schedule.command_type;
                form.querySelector('[name="schedule_command"]').value = schedule.command;
                form.querySelector('[name="schedule_type"]').value = schedule.schedule_type;
                form.querySelector('[name="interval_minutes"]').value = schedule.interval_minutes || 60;
                form.querySelector('[name="cron_expression"]').value = schedule.cron_expression || '';
                form.querySelector('[name="append_to_task_description"]').checked = schedule.append_to_task_description;
                form.querySelector('[name="is_enabled"]').checked = schedule.is_enabled;
                toggleScheduleType();
                currentScheduleResources = schedule.resources || [];
                renderResourceList();
            });
    } else {
        form.querySelector('[name="schedule_id"]').value = '';
        toggleScheduleType();
    }

    modal.style.display = 'flex';
}

function closeScheduleModal() {
    document.getElementById('schedule-modal').style.display = 'none';
}

function toggleScheduleType() {
    const type = document.querySelector('[name="schedule_type"]').value;
    document.getElementById('interval-group').style.display = type === 'interval' ? 'block' : 'none';
    document.getElementById('cron-group').style.display = type === 'cron' ? 'block' : 'none';
}

function toggleCommandType() {
    // Placeholder for any command type specific UI changes
}

function addResource() {
    const type = document.getElementById('resource_type_input').value;
    const path = document.getElementById('resource_path_input').value.trim();
    if (!path) return;

    currentScheduleResources.push({ resource_type: type, path: path });
    document.getElementById('resource_path_input').value = '';
    renderResourceList();
}

function removeResource(index) {
    currentScheduleResources.splice(index, 1);
    renderResourceList();
}

function renderResourceList() {
    const container = document.getElementById('resource-list');
    if (currentScheduleResources.length === 0) {
        container.innerHTML = '';
        return;
    }
    container.innerHTML = currentScheduleResources.map((r, i) => `
        <div class="resource-item">
            <span>${r.resource_type === 'folder' ? '📁' : '📄'} ${r.path}</span>
            <button type="button" onclick="removeResource(${i})">×</button>
        </div>
    `).join('');
}

async function saveSchedule(event) {
    event.preventDefault();
    const form = event.target;
    const scheduleId = form.querySelector('[name="schedule_id"]').value;
    const taskId = form.querySelector('[name="task_id_for_schedule"]').value;

    const data = {
        name: form.querySelector('[name="schedule_name"]').value,
        task_id: taskId ? parseInt(taskId) : null,
        command: form.querySelector('[name="schedule_command"]').value,
        command_type: form.querySelector('[name="command_type"]').value,
        schedule_type: form.querySelector('[name="schedule_type"]').value,
        interval_minutes: parseInt(form.querySelector('[name="interval_minutes"]').value) || null,
        cron_expression: form.querySelector('[name="cron_expression"]').value || null,
        append_to_task_description: form.querySelector('[name="append_to_task_description"]').checked,
        is_enabled: form.querySelector('[name="is_enabled"]').checked,
        resources: currentScheduleResources
    };

    try {
        const url = scheduleId ? `/api/schedules/${scheduleId}` : '/api/schedules';
        const method = scheduleId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeScheduleModal();
            if (taskId) {
                loadTaskSchedules(parseInt(taskId));
            }
        }
    } catch (error) {
        console.error('Error saving schedule:', error);
    }
}

async function editSchedule(scheduleId) {
    openScheduleForm(scheduleId);
}

async function runScheduleNow(scheduleId) {
    try {
        const response = await fetch(`/api/schedules/${scheduleId}/run`, { method: 'POST' });
        if (response.ok) {
            alert('スケジュールを実行しました');
            if (editingTaskId) {
                loadTaskSchedules(editingTaskId);
            }
        }
    } catch (error) {
        console.error('Error running schedule:', error);
    }
}

async function deleteSchedule(scheduleId) {
    if (!confirm('この定期実行設定を削除してもよろしいですか？')) return;

    try {
        const response = await fetch(`/api/schedules/${scheduleId}`, { method: 'DELETE' });
        if (response.ok && editingTaskId) {
            loadTaskSchedules(editingTaskId);
        }
    } catch (error) {
        console.error('Error deleting schedule:', error);
    }
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/history');
        if (response.ok) {
            const messages = await response.json();
            const container = document.getElementById('chat-messages');
            container.innerHTML = '';
            messages.forEach(msg => {
                addMessageToChat(msg.role, msg.content);
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Project Sidebar
let currentProjectId = null;

async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        if (response.ok) {
            const projects = await response.json();
            renderProjects(projects);
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function renderProjects(projects) {
    const container = document.getElementById('project-list');
    container.innerHTML = '';

    // All projects option
    const allItem = document.createElement('div');
    allItem.className = 'project-item' + (currentProjectId === null ? ' active' : '');
    allItem.innerHTML = '<span class="project-name">すべて</span>';
    allItem.onclick = () => selectProject(null);
    container.appendChild(allItem);

    projects.forEach(project => {
        const item = document.createElement('div');
        item.className = 'project-item' + (currentProjectId === project.id ? ' active' : '');
        item.innerHTML = `
            <span class="project-name" style="border-left: 4px solid ${project.color || '#3B82F6'}; padding-left: 0.5rem;">${project.name}</span>
            <div class="project-actions">
                <button onclick="event.stopPropagation(); editProject(${project.id}, '${project.name}', '${project.description || ''}', '${project.color || '#3B82F6'}')">✏️</button>
                <button onclick="event.stopPropagation(); deleteProject(${project.id})">🗑️</button>
            </div>
        `;
        item.onclick = () => selectProject(project.id);
        container.appendChild(item);
    });
}

function selectProject(projectId) {
    currentProjectId = projectId;
    console.log('selectProject called:', projectId);
    console.log('getBoardUrl:', getBoardUrl());
    loadProjects();
    htmx.ajax('GET', getBoardUrl(), { target: '#board-container', swap: 'innerHTML' });
}

// Project Modal
function openProjectModal() {
    document.getElementById('project-modal-title').textContent = 'プロジェクト作成';
    document.getElementById('project-form').reset();
    document.querySelector('#project-form [name="project_id"]').value = '';
    document.getElementById('project-modal').style.display = 'flex';
}

function closeProjectModal() {
    document.getElementById('project-modal').style.display = 'none';
}

function editProject(id, name, description, color) {
    document.getElementById('project-modal-title').textContent = 'プロジェクト編集';
    const form = document.getElementById('project-form');
    form.querySelector('[name="project_id"]').value = id;
    form.querySelector('[name="name"]').value = name;
    form.querySelector('[name="description"]').value = description;
    form.querySelector('[name="color"]').value = color;
    document.getElementById('project-modal').style.display = 'flex';
}

async function saveProject(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const projectId = formData.get('project_id');

    const data = {
        name: formData.get('name'),
        description: formData.get('description'),
        color: formData.get('color')
    };

    try {
        const url = projectId ? `/api/projects/${projectId}` : '/api/projects';
        const method = projectId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeProjectModal();
            loadProjects();
            htmx.ajax('GET', getBoardUrl(), { target: '#board-container', swap: 'innerHTML' });
        }
    } catch (error) {
        console.error('Error saving project:', error);
    }
}

async function deleteProject(projectId) {
    if (!confirm('このプロジェクトを削除してもよろしいですか？関連するタスクもすべて削除されます。')) return;

    try {
        const response = await fetch(`/api/projects/${projectId}`, { method: 'DELETE' });
        if (response.ok) {
            if (currentProjectId === projectId) {
                currentProjectId = null;
            }
            loadProjects();
            htmx.ajax('GET', getBoardUrl(), { target: '#board-container', swap: 'innerHTML' });
        }
    } catch (error) {
        console.error('Error deleting project:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initDragAndDrop();
    loadChatHistory();
    loadProjects();

    document.getElementById('board-container').addEventListener('htmx:afterSwap', () => {
        initDragAndDrop();
    });
});

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const taskModal = document.getElementById('task-modal');
    const projectModal = document.getElementById('project-modal');
    const scheduleModal = document.getElementById('schedule-modal');
    if (e.target === taskModal) {
        closeTaskModal();
    }
    if (e.target === projectModal) {
        closeProjectModal();
    }
    if (e.target === scheduleModal) {
        closeScheduleModal();
    }
});
