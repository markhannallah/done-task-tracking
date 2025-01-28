# Done - Task Tracking

A modern, efficient task tracking web application built with Flask and JavaScript.

## Features

- Create, update, and delete tasks
- Mark tasks as complete
- Organize tasks by priority and due date
- Clean, intuitive user interface
- Responsive design for mobile and desktop

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

- `app/`: Main application package
  - `static/`: Static files (CSS, JavaScript)
  - `templates/`: HTML templates
  - `models.py`: Database models
  - `routes.py`: Application routes
- `instance/`: Instance-specific files
- `requirements.txt`: Project dependencies
