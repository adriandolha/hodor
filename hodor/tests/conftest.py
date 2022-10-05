import logging
import os
import pytest
import mock

import hodor


@pytest.fixture(scope='session')
def config_valid():
    import json
    with open(f"{os.path.expanduser('~')}/.cloud-projects/hodor-local-integration.json", "r") as _file:
        json = dict(json.load(_file))
        print(json)
        for k, v in json.items():
            os.environ[k] = str(v)
        os.environ['db_setup'] = 'False'
        yield os.environ


@pytest.fixture()
def db_session(config_valid):
    with mock.patch('flask_sqlalchemy.SQLAlchemy.get_app'):
        with mock.patch('flask_sqlalchemy.SQLAlchemy.get_engine'):
            with mock.patch('flask_sqlalchemy.SQLAlchemy.create_session'):
                with mock.patch('flask_sqlalchemy.SignallingSession'):
                    with mock.patch('flask_sqlalchemy.SQLAlchemy.create_scoped_session'):
                        with mock.patch('hodor.db.session') as session:
                            yield session


@pytest.fixture()
def query_mock(db_session):
    with mock.patch('flask_sqlalchemy._QueryProperty.__get__') as q_mock:
        with mock.patch('hodor.repo.Transaction._db'):
            from hodor.repo import Transaction
            Transaction._db = None
            with mock.patch('hodor.repo.Transaction._session_maker'):
                with mock.patch('hodor.repo.Transaction.session'):
                    with mock.patch('hodor.repo.Transaction.pool'):
                        from hodor.models import User, Role, Permission, BlacklistToken
                        User.query = mock.MagicMock()
                        Role.query = mock.MagicMock()
                        Permission.query = mock.MagicMock()
                        BlacklistToken.query = mock.MagicMock()

                        def _filter_by(*args, **kwargs):
                            _mock = mock.MagicMock()
                            _mock.first.return_value = Permission.from_str(kwargs['name'])
                            return _mock

                        Permission.query.filter_by.side_effect = _filter_by
                        BlacklistToken.query.filter_by.return_value.first.return_value = None
                        yield q_mock


@pytest.fixture()
def login_valid_request(query_mock, user_admin_valid, role_admin_valid):
    from hodor.models import User, Role, Permission

    role = Role(id=role_admin_valid['id'], name=role_admin_valid['name'], default=role_admin_valid['default'],
                permissions=[Permission.from_str(perm) for perm in role_admin_valid['permissions']])
    Role.query.filter_by.return_value.first.return_value = role
    admin_user = User.from_dict(user_admin_valid)
    admin_user.role = role
    User.query.filter_by.return_value.filter_by.return_value.first.return_value = admin_user
    User.query.filter_by.return_value.first.return_value = admin_user
    yield admin_user


@pytest.fixture()
def user_add_request_valid(query_mock, user_admin_valid, role_admin_valid):
    from hodor.models import User, Role, Permission

    role = Role(id=role_admin_valid['id'], name=role_admin_valid['name'], default=role_admin_valid['default'],
                permissions=[Permission.from_str(perm) for perm in role_admin_valid['permissions']])
    Role.query.filter_by.return_value.first.return_value = role
    admin_user = User.from_dict(user_admin_valid)
    admin_user.role = role
    User.query.filter_by.return_value.filter_by.return_value.first.return_value = admin_user
    User.query.filter.return_value.first.return_value = None
    yield admin_user


@pytest.fixture()
def update_user_request_not_found(query_mock, user_admin_valid, role_admin_valid, user_valid):
    from hodor.models import User, Role, Permission

    role = Role(id=role_admin_valid['id'], name=role_admin_valid['name'], default=role_admin_valid['default'],
                permissions=[Permission.from_str(perm) for perm in role_admin_valid['permissions']])
    Role.query.filter_by.return_value.first.return_value = role
    admin_user = User.from_dict(user_admin_valid)
    admin_user.role = role

    User.query.filter_by.return_value.filter_by.return_value.first.return_value = admin_user

    def _filter_by(*args, **kwargs):
        if kwargs.get('username') == user_admin_valid['username']:
            _mock = mock.MagicMock()
            _mock.first.return_value = admin_user
            return _mock
        else:
            _mock = mock.MagicMock()
            _mock.first.return_value = None
            return _mock

    User.query.filter_by.side_effect = _filter_by
    yield user_admin_valid


@pytest.fixture()
def role_add_valid_request(query_mock, user_admin_valid, role_editor_valid):
    from hodor.models import User, Role
    orig_query = Role.query.filter_by.return_value

    def _filter_by(*args, **kwargs):
        if kwargs.get('name') == role_editor_valid['name']:
            _mock = mock.MagicMock()
            _mock.first.return_value = None
            return _mock
        return orig_query

    Role.query.filter_by.side_effect = _filter_by

    User.query.filter_by.return_value.filter_by.return_value.first.return_value = User.from_dict(
        user_admin_valid)
    User.query.filter_by.return_value.first.return_value = User.from_dict(
        user_admin_valid)
    yield user_admin_valid


@pytest.fixture()
def role_update_valid_request(query_mock, user_admin_valid, role_editor_valid):
    from hodor.models import User, Role, Permission
    orig_query = Role.query.filter_by.return_value
    role = Role(id=role_editor_valid['id'], name=role_editor_valid['name'], default=role_editor_valid['default'],
                permissions=[Permission.from_str(perm) for perm in role_editor_valid['permissions']])

    def _filter_by(*args, **kwargs):
        if kwargs.get('name') == role_editor_valid['name']:
            _mock = mock.MagicMock()
            _mock.first.return_value = role
            return _mock
        return orig_query

    Role.query.filter_by.side_effect = _filter_by

    User.query.filter_by.return_value.filter_by.return_value.first.return_value = User.from_dict(
        user_admin_valid)
    User.query.filter_by.return_value.first.return_value = User.from_dict(
        user_admin_valid)
    yield role


@pytest.fixture()
def role_get_valid_request(query_mock, user_admin_valid, role_editor_valid):
    from hodor.models import Permission, Role
    orig_query = Role.query.filter_by.return_value
    role = Role(id=role_editor_valid['id'],
                name=role_editor_valid['name'],
                permissions=[Permission.from_str(perm['name']) for perm in
                             role_editor_valid['permissions']])

    def _filter_by(*args, **kwargs):
        if kwargs.get('name') == role_editor_valid['name']:
            _mock = mock.MagicMock()
            _mock.first.return_value = role
            return _mock
        return orig_query

    Role.query.filter_by.side_effect = _filter_by
    yield role


@pytest.fixture()
def permission_add_valid_request(query_mock, user_admin_valid, permission_edit_books_valid):
    from hodor.models import User, Permission
    orig_query = Permission.query.filter_by.return_value

    def _filter_by(*args, **kwargs):
        if kwargs.get('name') == permission_edit_books_valid['name']:
            _mock = mock.MagicMock()
            _mock.first.return_value = None
            return _mock
        return orig_query

    Permission.query.filter_by.side_effect = _filter_by
    yield user_admin_valid


@pytest.fixture()
def role_add_existing_request(query_mock, user_admin_valid, role_editor_valid):
    from hodor.models import User, Role, Permission

    Role.query.filter_by.return_value.first.return_value = Role(id=role_editor_valid['id'],
                                                                name=role_editor_valid['name'],
                                                                permissions=[Permission.from_str(perm) for perm in
                                                                             role_editor_valid['permissions']])
    User.query.filter_by.return_value.filter_by.return_value.first.return_value = User.from_dict(
        user_admin_valid)
    User.query.filter_by.return_value.first.return_value = User.from_dict(
        user_admin_valid)
    Permission.query.filter_by.return_value.first.return_value = Permission.from_str('books:add')
    yield user_admin_valid


@pytest.fixture()
def signup_valid_request(query_mock, user_admin_valid, role_admin_valid):
    from hodor.models import User, Role, Permission
    Role.query.filter_by.return_value.first.return_value = Role(id=role_admin_valid['id'],
                                                                name=role_admin_valid['name'],
                                                                permissions=[Permission.from_str(perm) for perm in
                                                                             role_admin_valid['permissions']])
    User.query.filter_by.return_value.first.return_value = None

    yield user_admin_valid


@pytest.fixture()
def app(db_session):
    import hodor.app
    app = hodor.app.create_flask_app()
    LOGGER = logging.getLogger('lorem-ipsum-auth')
    LOGGER.setLevel(logging.DEBUG)
    app.config.update({
        "TESTING": True,
    })
    # yield app
    with app.test_request_context():
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def user_admin_valid():
    import werkzeug.security
    yield {"username": 'admin',
           "password_hash": werkzeug.security.generate_password_hash('fake_admin_password'),
           "email": "admin@yahoo.com",
           "login_type": "basic",
           "role_id": 1,
           "id": 1
           }


@pytest.fixture()
def user_valid():
    import werkzeug.security
    yield {"username": 'admin',
           "password_hash": werkzeug.security.generate_password_hash('fake_admin_password'),
           "email": "admin@yahoo.com",
           "login_type": "basic",
           "role_id": 2,
           "id": 2
           }


@pytest.fixture(scope='session')
def user_valid1():
    import werkzeug.security
    yield {"username": 'test_user1',
           "password_hash": werkzeug.security.generate_password_hash('fake_admin_password'),
           "email": "test_user1@yahoo.com",
           "login_type": "basic",
           "role_id": 2,
           "id": 2
           }


@pytest.fixture(scope='session')
def new_user_valid():
    yield {"username": 'test_user1',
           "password": 'valid_password',
           "email": "test_user1@yahoo.com",
           "login_type": "basic",
           "role_id": 2,
           "id": 2
           }


@pytest.fixture()
def role_user_valid():
    yield {
        "name": "ROLE_USER",
        "id": 2,
        "permissions": ['books:add', 'books:read', 'books:write', 'users:profile']
    }


@pytest.fixture()
def role_admin_valid():
    yield {
        "name": "ROLE_USER",
        "id": 2,
        "default": False,
        "permissions": ['books:add', 'books:read', 'books:write', 'users:profile', 'users:admin']
    }


@pytest.fixture()
def permission_edit_books_valid():
    yield {
        "name": "books:edit",
        "id": 'books:edit'}


@pytest.fixture()
def role_editor_valid():
    from hodor.models import Permissions, Permission
    yield {
        "name": "ROLE_EDITOR",
        "id": 5,
        "default": False,
        "permissions": [Permission.from_enum(Permissions.BOOKS_READ).as_dict(),
                        Permission.from_enum(Permissions.BOOKS_WRITE).as_dict(),
                        Permission.from_enum(Permissions.BOOKS_ADD).as_dict(),
                        Permission.from_enum(Permissions.USERS_PROFILE).as_dict(),
                        ]
    }


def issue_token(user: dict, role: dict) -> str:
    from hodor.models import User, Permission, Role
    from hodor.auth import issue_token_for_user
    role = Role(id=user['id'], name=role['name'],
                permissions=[Permission.from_str(perm) for perm in role['permissions']])
    Role.query.filter_by.return_value.first.return_value = role
    _user = User.from_dict(user)
    _user.role = role
    User.query.filter_by.return_value.filter_by.return_value.first.return_value = _user
    User.query.filter_by.return_value.first.return_value = _user
    return issue_token_for_user(_user)


@pytest.fixture()
def admin_access_token(config_valid, user_admin_valid, role_admin_valid, query_mock):
    return issue_token(user_admin_valid, role_admin_valid)


@pytest.fixture()
def user_access_token(config_valid, user_valid, role_user_valid, query_mock):
    return issue_token(user_valid, role_user_valid)
