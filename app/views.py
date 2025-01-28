from flask import Blueprint, render_template, request, jsonify
from .models import Task, DailyXP
from . import db
from datetime import datetime, timedelta
import calendar

views = Blueprint('views', __name__)

MIT_POINTS = 50
TASK_SIZES = {
    'small': 5,
    'medium': 10,
    'large': 15,
    'xl': 25
}

def get_start_of_week(date):
    """Get the Sunday that starts the week containing the given date."""
    return date - timedelta(days=date.weekday() + 1)

def format_relative_time(days_ago):
    """Format relative time with proper pluralization and time units."""
    if days_ago == 0:
        return 'Today'
    elif days_ago == 1:
        return 'Yesterday'
    elif days_ago < 7:
        return f"{days_ago} days ago"
    elif days_ago < 30:
        weeks = days_ago // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif days_ago < 365:
        months = days_ago // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = days_ago // 365
        return f"{years} year{'s' if years != 1 else ''} ago"

@views.route('/')
def home():
    # Get current date information
    today = datetime.now()
    date_info = {
        'day': today.strftime('%A'),
        'date': today.strftime('%B %d, %Y')
    }
    
    # Get tasks sorted by completion status (open first) then by order
    mit_tasks = Task.query.filter_by(task_type='mit').order_by(Task.completed, Task.order, Task.id).all()
    regular_tasks = Task.query.filter_by(task_type='regular').order_by(Task.completed, Task.order, Task.id).all()
    
    # Count open tasks
    open_regular_tasks = sum(1 for task in regular_tasks if not task.completed)
    open_mit_tasks = sum(1 for task in mit_tasks if not task.completed)
    total_open = open_regular_tasks + open_mit_tasks
    
    # Calculate task distribution percentages
    mit_percentage = round((open_mit_tasks / total_open * 100) if total_open > 0 else 0)
    regular_percentage = round((open_regular_tasks / total_open * 100) if total_open > 0 else 0)
    
    # Calculate completion rate
    total_tasks = total_open + sum(1 for task in regular_tasks + mit_tasks if task.completed)
    completion_rate = round((1 - total_open / total_tasks * 100) if total_tasks > 0 else 0)
    
    total_xp = sum(task.points for task in Task.query.filter_by(completed=True).all())
    
    # Get the current week's data (Sunday to Saturday)
    today = datetime.utcnow().date()
    start_date = get_start_of_week(today)
    end_date = start_date + timedelta(days=6)
    
    # Get the week's XP data
    weekly_xp = DailyXP.query.filter(
        DailyXP.date >= start_date,
        DailyXP.date <= end_date
    ).order_by(DailyXP.date).all()
    
    # Get completed tasks by date for the week
    completed_tasks = Task.query.filter(
        Task.completed == True,
        Task.completed_at >= start_date,
        Task.completed_at <= end_date + timedelta(days=1)
    ).all()
    
    # Group completed tasks by date
    tasks_by_date = {}
    for task in completed_tasks:
        date = task.completed_at.date()
        if date not in tasks_by_date:
            tasks_by_date[date] = 0
        tasks_by_date[date] += 1
    
    # Create a mapping of dates to XP
    xp_by_date = {xp.date: xp.xp_earned for xp in weekly_xp}
    
    # Generate weekly data with proper day labels
    weekly_xp_data = []
    current_date = start_date
    max_daily_xp = max((xp.xp_earned for xp in weekly_xp), default=0)
    suggested_max = ((max_daily_xp // 50) + 1) * 50 if max_daily_xp > 0 else 50  # Default to 50 if no XP
    
    while current_date <= end_date:
        is_today = current_date == today
        day_name = calendar.day_abbr[current_date.weekday()]
        weekly_xp_data.append({
            'date': day_name,
            'full_date': current_date.strftime('%Y-%m-%d'),
            'xp': xp_by_date.get(current_date, 0),
            'is_today': is_today,
            'tasks_completed': tasks_by_date.get(current_date, 0)
        })
        current_date += timedelta(days=1)
    
    # Get all-time XP data for cumulative chart
    all_daily_xp = DailyXP.query.order_by(DailyXP.date).all()
    cumulative_xp_data = []
    running_total = 0
    total_tasks_completed = 0
    
    # Get all completed tasks for cumulative data
    all_completed_tasks = Task.query.filter_by(completed=True).order_by(Task.completed_at).all()
    tasks_completed_by_date = {}
    for task in all_completed_tasks:
        if task.completed_at:  # Make sure completed_at is not None
            date = task.completed_at.date()
            if date not in tasks_completed_by_date:
                tasks_completed_by_date[date] = 0
            tasks_completed_by_date[date] += 1
    
    for daily in all_daily_xp:
        running_total += daily.xp_earned
        days_ago = (today - daily.date).days
        daily_tasks = tasks_completed_by_date.get(daily.date, 0)
        total_tasks_completed += daily_tasks
        
        cumulative_xp_data.append({
            'date': daily.date.strftime('%Y-%m-%d'),
            'relative_time': format_relative_time(days_ago),
            'xp': running_total,
            'daily_xp': daily.xp_earned,
            'daily_tasks': daily_tasks,
            'total_tasks': total_tasks_completed
        })
    
    # Calculate some stats for the charts
    week_total = sum(xp_by_date.values())
    daily_average = week_total / 7 if len(weekly_xp) > 0 else 0  # Only calculate average if we have data
    week_tasks_completed = sum(tasks_by_date.values())
    
    return render_template(
        "home.html",
        regular_tasks=regular_tasks,
        mit_tasks=mit_tasks,
        total_xp=total_xp,
        weekly_xp_data=weekly_xp_data,
        cumulative_xp_data=cumulative_xp_data,
        task_sizes=TASK_SIZES,
        mit_points=MIT_POINTS,
        week_total=week_total,
        daily_average=daily_average,
        suggested_max=suggested_max,
        open_regular_tasks=open_regular_tasks,
        open_mit_tasks=open_mit_tasks,
        week_tasks_completed=week_tasks_completed,
        total_tasks_completed=total_tasks_completed,
        mit_percentage=mit_percentage,
        regular_percentage=regular_percentage,
        completion_rate=completion_rate,
        date_info=date_info
    )

@views.route('/add-task', methods=['POST'])
def add_task():
    data = request.json
    title = data.get('title')
    task_type = data.get('task_type', 'regular')
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    try:
        if task_type == 'mit':
            points = MIT_POINTS
        else:
            size = data.get('size', 'medium')
            points = TASK_SIZES.get(size, TASK_SIZES['medium'])
        
        new_task = Task(
            title=title,
            points=points,
            task_type=task_type
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Task added successfully",
            "taskId": new_task.id,
            "points": points,
            "title": title,
            "task_type": task_type
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@views.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        if not task.completed:
            task.completed = True
            task.completed_at = datetime.utcnow()
            # Add XP to daily tracking
            DailyXP.add_xp(task.points)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Task completed!",
                "points": task.points
            }), 200
        return jsonify({"success": False, "message": "Task was already completed"}), 200
    return jsonify({"success": False, "error": "Task not found"}), 404

@views.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        # If task was completed, remove XP from daily tracking
        if task.completed and task.completed_at:
            daily_xp = DailyXP.query.filter_by(date=task.completed_at.date()).first()
            if daily_xp:
                daily_xp.xp_earned = max(0, daily_xp.xp_earned - task.points)
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Task deleted successfully"
        }), 200
    return jsonify({"success": False, "error": "Task not found"}), 404

@views.route('/reorder-tasks', methods=['POST'])
def reorder_tasks():
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        task_type = data.get('task_type')
        
        # Update task order
        for index, task_id in enumerate(task_ids):
            task = Task.query.get(task_id)
            if task and task.task_type == task_type:
                task.order = index
        
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
