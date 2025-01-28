#!/bin/bash
kill -9 $(lsof -t -i:5001) 2>/dev/null || true
source venv/bin/activate
FLASK_DEBUG=1 flask run --host=localhost --port=5001 --reload
