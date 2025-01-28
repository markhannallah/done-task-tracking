from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your secret key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views, init_db
    from .models import Task, DailyXP

    app.register_blueprint(views, url_prefix='/')

    with app.app_context():
        if not path.exists('app/' + DB_NAME):
            db.create_all()
            print('Created Database!')
        
        # Initialize new columns
        init_db()

    return app
