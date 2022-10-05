import os

import flask
import pytest
import requests
from requests.auth import HTTPBasicAuth

from hodor.serializers import from_json


@pytest.fixture()
def config_valid():
    import json
    _config = {}
    with open(f"{os.path.expanduser('~')}/.cloud-projects/lorem-ipsum-local.json", "r") as _file:
        json = dict(json.load(_file))
        print(json)
        for k, v in json.items():
            os.environ[k] = str(v)
            _config[k] = v
    return _config


@pytest.fixture()
def admin_token_valid(config_valid):
    yield os.getenv('admin_token')


@pytest.fixture()
def user_token_valid(config_valid):
    yield os.getenv('user_token')


@pytest.fixture()
def user_valid1(config_valid, admin_access_token):
    username = 'test_user1'
    _response = delete_user(admin_access_token, config_valid, username)
    assert _response.status_code == 204
    yield {"username": 'test_user1',
           "password": config_valid['test_password'],
           "email": "test_user1@gmail.com"
           }
    _response = delete_user(admin_access_token, config_valid, username)
    assert _response.status_code == 204


def delete_user(admin_access_token, config_valid, username):
    _response = requests.delete(url=f'{config_valid["root_url"]}/api/users/{username}',
                                headers={'Content-Type': 'application/json',
                                         'Authorization': f'Bearer {admin_access_token}'}, timeout=3,
                                )
    return _response


@pytest.fixture()
def user_valid2():
    yield {"username": 'test_user2',
           "password": 'pwd',
           "email": "test_user2@gmail.com"
           }


@pytest.fixture()
def new_user_valid():
    yield {"username": 'test_user3',
           "password": 'valid_password',
           "email": "test_user3@yahoo.com",
           "login_type": "basic",
           "role_id": 2,
           "id": 2
           }


@pytest.fixture()
def metrics_request_no_fields(config_valid):
    import app
    with app.app.test_request_context():
        yield flask.request.args


@pytest.fixture()
def user_access_token(config_valid):
    username = config_valid['guest_user']
    password = config_valid['guest_password']
    return _get_access_token(config_valid, password, username)


def _get_access_token(config_valid, password, username):
    _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/signin',
                             headers={'Content-Type': 'application/json'}, timeout=3,
                             auth=HTTPBasicAuth(username, password))
    print(_response.content)
    assert _response.status_code == 200
    _response_data = from_json(_response.content.decode('utf-8'))
    print(_response_data)
    access_token_ = _response_data['access_token']
    assert access_token_
    return access_token_


@pytest.fixture()
def admin_access_token(config_valid):
    username = config_valid['admin_user']
    password = config_valid['admin_password']
    return _get_access_token(config_valid, password, username)


@pytest.fixture()
def admin_access_token_logout(config_valid):
    username = config_valid['admin_user']
    password = config_valid['admin_password']
    access_token = _get_access_token(config_valid, password, username)
    yield access_token


@pytest.fixture()
def role_editor_valid():
    yield {'default': False, 'id': None, 'name': 'ROLE_EDITOR',
           'permissions': [{'id': 'books:read', 'name': 'books:read'}, {'id': 'books:write', 'name': 'books:write'},
                           {'id': 'books:add', 'name': 'books:add'}, {'id': 'users:profile', 'name': 'users:profile'}]}


@pytest.fixture()
def role_update_valid():
    yield {'default': False, 'id': None, 'name': 'ROLE_TEST',
           'permissions': [{'id': 'books:read', 'name': 'books:read'}, {'id': 'books:write', 'name': 'books:write'},
                           {'id': 'books:add', 'name': 'books:add'}, {'id': 'users:profile', 'name': 'users:profile'}]}


@pytest.fixture()
def role_admin_valid():
    yield {'default': False, 'id': None, 'name': 'ROLE_ADMIN',
           'permissions': [{'id': 'books:add', 'name': 'books:add'},
                           {'id': 'books:read', 'name': 'books:read'},
                           {'id': 'books:write', 'name': 'books:write'},
                           {'id': 'users:admin', 'name': 'users:admin'},
                           {'id': 'users:profile', 'name': 'users:profile'}]}


@pytest.fixture()
def permission_edit_books_valid():
    yield {'id': 'books:edit', 'name': 'books:edit',
           }
