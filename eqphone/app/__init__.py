"""
Initialization flask application
"""
import os
from flask import Flask, render_template
from flask_cors import CORS

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    for cfg in app.config:
        if isinstance(app.config[cfg], str):
            app.config[cfg] = app.config[cfg].replace('{instance}', app.instance_path)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # apply the blueprints to the app

    os.environ['BLUEPRINTS_TYPES'] = app.config.get('BLUEPRINTS_TYPES', "")

    from app import eqphone

    app.register_blueprint(eqphone.BP)

    eqphone.init_app(app)


    @app.route('/')
    def show_index():
        """
        index page render
        """
        return render_template('index.html')

    return app
