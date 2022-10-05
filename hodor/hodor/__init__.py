import datetime
import logging
import platform
from functools import lru_cache

import boto3
from flask_sqlalchemy import SQLAlchemy

import hodor

db = SQLAlchemy()


def get_ssm_secret(parameter_name, decrypt=True):
    ssm = boto3.client("ssm")
    return ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=decrypt
    )


def configure_logging():
    logging.basicConfig(format='%(asctime)s.%(msecs)03dZ %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    LOGGER = logging.getLogger('lorem-ipsum-auth')
    LOGGER.setLevel(logging.DEBUG)
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    # LOGGER.addHandler(logging.StreamHandler())
    LOGGER.info('logging configured...')


class AppContext:
    def __init__(self):
        from hodor.repo import transaction, UserRepo, TransactionManager
        from hodor.service import MetricsService, UserService
        from hodor.config import get_config
        from hodor.service import Authenticator
        self._authenticator = None

        self.config = get_config()
        self.transaction_manager = TransactionManager(self)
        self.user_repo = UserRepo(self)
        self.user_service = UserService(self)
        self.metrics_service = MetricsService(self)

    @property
    def authenticator(self):
        return self._authenticator

    def init(self):
        pass
        # from hodor.repo import db_setup
        # with self.transaction_manager.transaction:
        #     db_setup(self)

    @staticmethod
    def local_context():
        app_context = AppContext()
        from hodor.authentication import Auth0Authenticator
        app_context._authenticator = Auth0Authenticator(app_context)
        return app_context


def setup(app_context: AppContext):
    LOGGER = logging.getLogger('lorem-ipsum')
    LOGGER.debug('Running database setup...')
    app_context.init()


@lru_cache()
def create_app() -> AppContext:
    configure_logging()
    LOGGER = logging.getLogger('lorem-ipsum-auth')
    LOGGER.info('Application init...')
    LOGGER.info(f'Platform: {platform.python_implementation()}')
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    LOGGER.info(f'Start time: {now}')
    app_context = AppContext.local_context()
    setup(app_context)
    return app_context


def create_app_context() -> AppContext:
    _app_context = AppContext.local_context()
    return _app_context
