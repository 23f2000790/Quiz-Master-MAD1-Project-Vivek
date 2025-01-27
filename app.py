from flask import Flask
from controllers.database import db

app = None

def create_app():
    app = Flask(__name__)
    app.secret_key = "app-by-vivek"
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quizmasterdata.sqlite3"
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

from controllers.main import *


if __name__ == "__main__":
    app.run()

