// Task completion handling
document.addEventListener('click', async function(e) {
    const button = e.target.closest('.complete-task');
    if (!button) return;

    try {
        const taskItem = button.closest('.list-group-item');
        if (!taskItem) {
            console.error('Could not find task item');
            return;
        }

        const taskId = taskItem.dataset.taskId;
        if (!taskId) {
            console.error('No task ID found');
            return;
        }

        button.disabled = true; // Prevent double-clicks

        const response = await fetch('/complete-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ taskId: taskId })
        });

        const data = await response.json();
        
        if (data.success) {
            // Get the task section (mit or regular)
            const taskSection = taskItem.closest('.card-body');
            const isRegular = taskSection.querySelector('.regular-header') !== null;
            const taskType = isRegular ? 'regular' : 'mit';
            
            // Remove task from active section
            taskItem.remove();
            
            // Create completed task element
            const completedTaskHtml = `
                <div class="list-group-item completed-task" data-task-id="${taskId}">
                    <div class="task-info">
                        <span class="task-title">${taskItem.querySelector('.task-title').textContent}</span>
                        <span class="task-metadata">
                            <span class="task-points">${taskItem.querySelector('.task-points').textContent}</span>
                            <span class="completion-date" title="${new Date().toISOString()}">
                                ${new Date().toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true})}
                            </span>
                        </span>
                    </div>
                </div>
            `;
            
            // Find or create completed section
            let completedSection = taskSection.querySelector('.completed-section');
            if (!completedSection) {
                const completedSectionHtml = `
                    <div class="completed-section mt-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="text-muted">Completed</h6>
                            <span class="task-count text-muted" id="completed-${taskType}-count">1 completed</span>
                        </div>
                        <div class="list-group" id="completed-${taskType}-tasks"></div>
                        <div class="text-center mt-2">
                            <button class="btn btn-sm btn-outline-secondary archive-tasks" data-task-type="${taskType}">
                                Archive Completed Tasks
                            </button>
                        </div>
                    </div>
                `;
                taskSection.insertAdjacentHTML('beforeend', completedSectionHtml);
                completedSection = taskSection.querySelector('.completed-section');
            }
            
            // Add completed task to the completed section
            const completedTasksList = completedSection.querySelector('.list-group');
            completedTasksList.insertAdjacentHTML('afterbegin', completedTaskHtml);
            
            // Update task counts
            updateTaskCounts();
            
            // Show success message
            showToast('Task completed!', 'success');
        } else {
            console.error('Failed to complete task:', data.error);
            showToast('Failed to complete task: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showToast('Error completing task. Please try again.', 'error');
    } finally {
        if (button) {
            button.disabled = false;
        }
    }
});

// Archive tasks handling
document.addEventListener('click', async function(e) {
    const button = e.target.closest('.archive-tasks');
    if (!button) return;

    const taskType = button.dataset.taskType;
    button.disabled = true;

    try {
        const response = await fetch('/archive-tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ taskType: taskType })
        });

        const data = await response.json();
        
        if (data.success) {
            // Remove the completed section
            const completedSection = button.closest('.completed-section');
            if (completedSection) {
                completedSection.remove();
            }
            
            // Update task counts
            updateTaskCounts();
            
            // Show success message
            showToast('Tasks archived successfully!', 'success');
        } else {
            console.error('Failed to archive tasks:', data.error);
            showToast('Failed to archive tasks: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error archiving tasks:', error);
        showToast('Error archiving tasks. Please try again.', 'error');
    } finally {
        button.disabled = false;
    }
});

// Update task counts
function updateTaskCounts() {
    const elements = {
        'mit-count': '#mit-tasks .list-group-item:not(.completed-task)',
        'regular-count': '#regular-tasks .list-group-item:not(.completed-task)',
        'completed-mit-count': '#completed-mit-tasks .list-group-item',
        'completed-regular-count': '#completed-regular-tasks .list-group-item'
    };

    for (const [id, selector] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) {
            const count = document.querySelectorAll(selector).length;
            const label = id.includes('completed') ? ' completed' : ' active';
            element.textContent = `${count}${label}`;
        }
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }, 100);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateTaskCounts();
});
