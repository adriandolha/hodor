import base64
import os
from functools import lru_cache
import logging

import boto3

DEFAULT_CONFIGS = {
    'connection_pool_minconn': 30,
    'connection_pool_maxconn': 40
}


@lru_cache()
def get_config():
    aurora_password = os.getenv('aurora_password')
    if os.getenv('app_env') == 'aws':
        session = boto3.session.Session()
        kms = session.client('kms')
        aurora_password = kms.decrypt(CiphertextBlob=base64.b64decode(aurora_password))['Plaintext'].decode('utf-8')
    _config = dict(DEFAULT_CONFIGS)
    _config.update({
        'aurora_host': os.getenv('aurora_host'),
        'aurora_user': os.getenv('aurora_user'),
        'aurora_port': int(os.getenv('aurora_port', default=5432)),
        'aurora_password': aurora_password,
        'database_name': os.getenv('database_name'),
        'password_encryption_key': os.getenv('password_encryption_key'),
        'admin_password': os.getenv('admin_password'),
        'admin_user': os.getenv('admin_user'),
        'guest_password': os.getenv('guest_password'),
        'guest_user': os.getenv('guest_user'),
        'google_client_id': os.getenv('google_client_id'),
        'google_client_secret': os.getenv('google_client_secret'),
        'db_setup': True if os.getenv('db_setup', 'True') == 'True' else False,
        'jwk_public_key': base64.b64decode(os.getenv('jwk_public_key')) if os.getenv(
            'jwk_public_key') else None,
        'jwk_private_key': base64.b64decode(os.getenv('jwk_private_key')) if os.getenv(
            'jwk_private_key') else None,
        'jwk_public_key_path': os.getenv('jwk_public_key_path', '/jwk/certs/public.key'),
        'jwk_private_key_path': os.getenv('jwk_private_key_path', '/jwk/certs/private.key')
    })
    LOGGER = logging.getLogger('lorem-ipsum')
    LOGGER.debug('Configuration:')
    for config_name in _config.keys():
        if 'password' not in config_name:
            LOGGER.debug(f'{config_name}={_config[config_name]}')
    return _config
