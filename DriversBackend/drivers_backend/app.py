from flask import Flask
from flask_restplus import Api
from flask_cors import CORS


def create_app():
    from drivers_backend.api_namespace import api_namespace
    from drivers_backend.admin_namespace import admin_namespace

    application = Flask(__name__)
    CORS(application)
    api = Api(application, version='0.1', title='Drivers Backend API',
              description='A Zeno CRUD API')

    from drivers_backend.db import db, db_config
    application.config['RESTPLUS_MASK_SWAGGER'] = False
    application.config.update(db_config)
    db.init_app(application)
    application.db = db

    api.add_namespace(api_namespace)
    api.add_namespace(admin_namespace)

    return application
