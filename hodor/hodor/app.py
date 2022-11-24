import logging

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

import gevent_psycopg2
import hodor
from hodor import db
from hodor.auth import token_auth, users, ExceptionHandlers
from hodor.google_oauth import google_oauth
from hodor.models import Role, User, Permission


def prepare_orm_for_gevent():
    """
    In order to make psycopg2 work with gevent, we need to apply this patch, otherwise all worker connections will use
    only one connection which might cause serious issues in production.
    Also, the patch needs to be applied before creating the db engine.
    """
    gevent_psycopg2.monkey_patch()


def create_flask_app():
    prepare_orm_for_gevent()
    app = Flask(__name__)
    _app_context = hodor.create_app()
    _config = _app_context.config
    LOGGER = logging.getLogger('lorem-ipsum-auth')
    app.config.update({
        'SECRET_KEY': _app_context.user_service.secret_key(),
        'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': _app_context.transaction_manager.database_connection_string,
    })

    if _app_context.config['db_setup']:
        @app.before_first_request
        def create_tables():
            db.create_all()
            LOGGER.debug('Setting roles...')
            Permission.insert_permissions()
            Role.insert_roles()
            LOGGER.debug('Setting users...')
            User.insert_users(_config)

    db.init_app(app)
    app.register_blueprint(google_oauth, url_prefix='/api/google')
    app.register_blueprint(token_auth, url_prefix='/api')
    app.register_blueprint(users, url_prefix='/api/users')
    swaggerui_blueprint = get_swaggerui_blueprint('/api/docs', '/api/spec')
    app.register_blueprint(swaggerui_blueprint)
    app.url_map.strict_slashes = False
    ExceptionHandlers(app)

    @app.route('/health', methods=['GET'])
    def health():
        LOGGER.info('Checking system health...')
        return 'all_good'

    @app.route('/', methods=['GET'])
    def home():
        LOGGER.info('Checking system health...')
        return 'all_good'

    LOGGER.debug(app.config)
    return app
