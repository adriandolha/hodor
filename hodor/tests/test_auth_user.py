import json
import os

from mock.mock import MagicMock

from hodor.models import LoginType, User, Role

os.environ['env'] = 'test'


class TestAuthUser:
    def test_user_signin(self, client, config_valid, login_valid_request, user_admin_valid, role_admin_valid,
                         query_mock):
        _response = client.post('/api/auth/signin', json={'username': config_valid['admin_user'],
                                                          'password': config_valid['admin_password']})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        assert data['access_token']
        assert data['username'] == user_admin_valid['username']
        assert len(data['roles']) == 1
        assert role_admin_valid['name'] in data['roles']
        assert len(data['permissions']) == 5
        assert data['permissions'] == ['books:add', 'books:read', 'books:write', 'users:profile', 'users:admin']

    def test_user_signin_invalid_password(self, client, config_valid, login_valid_request, user_admin_valid,
                                          role_admin_valid, query_mock):
        _response = client.post('/api/auth/signin', json={'username': config_valid['admin_user'],
                                                          'password': 'wrong_password'})
        assert _response.status_code == 401
        data = json.loads(_response.data.decode('utf-8'))
        assert data == 'Invalid username or password'

    def test_user_signup(self, client, config_valid, signup_valid_request, user_admin_valid, role_admin_valid,
                         query_mock):
        _response = client.post('/api/auth/signup', json={'username': config_valid['admin_user'],
                                                          'email': user_admin_valid['email'],
                                                          'password': config_valid['admin_password']})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        assert data['access_token']
        assert data['username'] == user_admin_valid['username']
        assert len(data['roles']) == 1
        assert role_admin_valid['name'] in data['roles']

    def test_user_signup_user_already_registered(self, client, config_valid, login_valid_request, user_admin_valid,
                                                 role_admin_valid,
                                                 query_mock):
        _response = client.post('/api/auth/signup', json={'username': config_valid['admin_user'],
                                                          'password': config_valid['admin_password']})
        assert _response.status_code == 400
        data = json.loads(_response.data.decode('utf-8'))
        assert data == 'User already registered'

    def test_user_profile(self, client, config_valid, login_valid_request, user_valid, role_admin_valid,
                          query_mock, user_access_token):
        _response = client.get('/api/auth/profile', headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        # assert data['access_token']
        assert data['username'] == user_valid['username']
        assert len(data['roles']) == 1
        assert role_admin_valid['name'] in data['roles']
        assert len(data['permissions']) == 4
        assert data['permissions'] == ['books:add', 'books:read', 'books:write', 'users:profile']

    def test_user_get(self, client, config_valid, login_valid_request, user_valid, role_admin_valid,
                      query_mock, admin_access_token):
        _response = client.get(f'/api/users/{user_valid["username"]}',
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        # assert data['access_token']
        assert data['username'] == user_valid['username']
        assert role_admin_valid['name'] == data['role']['name']
        assert len(data['role']['permissions']) == 5
        print(data['role']['permissions'])
        assert data['role']['permissions'] == [{'id': 'books:add', 'name': 'books:add'},
                                               {'id': 'books:read', 'name': 'books:read'},
                                               {'id': 'books:write', 'name': 'books:write'},
                                               {'id': 'users:profile', 'name': 'users:profile'},
                                               {'id': 'users:admin', 'name': 'users:admin'}]

    def test_get_users(self, client, config_valid, login_valid_request, user_valid, role_admin_valid,
                       query_mock, admin_access_token):
        from hodor.models import User
        User.query.all.return_value = [login_valid_request]
        _response = client.get(f'/api/users',
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        assert data['total'] == 1
        _user = data['items'][0]
        # assert data['access_token']
        assert _user['username'] == user_valid['username']
        assert role_admin_valid['name'] == _user['role']['name']
        assert len(_user['role']['permissions']) == 5
        print(_user['role']['permissions'])
        assert _user['role']['permissions'] == [{'id': 'books:add', 'name': 'books:add'},
                                                {'id': 'books:read', 'name': 'books:read'},
                                                {'id': 'books:write', 'name': 'books:write'},
                                                {'id': 'users:profile', 'name': 'users:profile'},
                                                {'id': 'users:admin', 'name': 'users:admin'}]

    def test_user_update(self, client, config_valid, login_valid_request, user_valid, role_admin_valid,
                         query_mock, admin_access_token, role_editor_valid):
        user_valid['role'] = role_editor_valid
        _response = client.put(f'/api/users/{user_valid["username"]}',
                               headers={'Authorization': f'Bearer {admin_access_token}'}, json=user_valid)
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        # assert data['access_token']
        assert data['username'] == user_valid['username']
        assert role_admin_valid['name'] == data['role']['name']
        assert len(data['role']['permissions']) == 5
        print(data['role']['permissions'])
        assert data['role']['permissions'] == [{'id': 'books:add', 'name': 'books:add'},
                                               {'id': 'books:read', 'name': 'books:read'},
                                               {'id': 'books:write', 'name': 'books:write'},
                                               {'id': 'users:profile', 'name': 'users:profile'},
                                               {'id': 'users:admin', 'name': 'users:admin'}]

    def test_user_update_not_found(self, client, config_valid, update_user_request_not_found, user_valid1,
                                   role_admin_valid,
                                   admin_access_token, role_editor_valid):
        from hodor.models import User
        User.query.filter_by.return_value.first.return_value = None
        user_valid1['role'] = role_editor_valid
        _response = client.put(f'/api/users/{user_valid1["username"]}',
                               headers={'Authorization': f'Bearer {admin_access_token}'}, json=user_valid1)
        assert _response.status_code == 404

    def test_get_users_permission_required(self, client, config_valid, login_valid_request, user_valid,
                                           role_admin_valid,
                                           user_access_token, query_mock):
        from hodor.models import User
        User.query.all.return_value = [login_valid_request]

        _response = client.get(f'/api/users', headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_user_add(self, client, config_valid, user_add_request_valid, new_user_valid, role_admin_valid,
                      query_mock, admin_access_token, role_editor_valid, db_session):
        new_user_valid['role'] = role_editor_valid
        _response = client.post(f'/api/users',
                                headers={'Authorization': f'Bearer {admin_access_token}'}, json=new_user_valid)
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        # assert data['access_token']
        assert data['username'] == new_user_valid['username']
        assert role_admin_valid['name'] == data['role']['name']
        assert len(data['role']['permissions']) == 5
        print(data['role']['permissions'])
        assert data['role']['permissions'] == [{'id': 'books:add', 'name': 'books:add'},
                                               {'id': 'books:read', 'name': 'books:read'},
                                               {'id': 'books:write', 'name': 'books:write'},
                                               {'id': 'users:profile', 'name': 'users:profile'},
                                               {'id': 'users:admin', 'name': 'users:admin'}]
        new_user = db_session.add.call_args[0][0]
        new_user.verify_password(new_user_valid['password'])
        assert new_user.username == new_user_valid['username']
        assert new_user.email == new_user_valid['email']
        assert new_user.login_type == LoginType.BASIC

    def test_user_add_already_registered(self, client, config_valid, user_add_request_valid, new_user_valid,
                                         role_admin_valid,
                                         query_mock, admin_access_token, role_editor_valid, db_session):
        new_user_valid['role'] = role_editor_valid
        User.query.filter.return_value.first.return_value = MagicMock()

        _response = client.post(f'/api/users',
                                headers={'Authorization': f'Bearer {admin_access_token}'}, json=new_user_valid)
        assert _response.status_code == 400
        data = json.loads(_response.data.decode('utf-8'))
        assert data == 'User already registered.'

    def test_user_add_role_not_found(self, client, config_valid, user_add_request_valid, new_user_valid, role_admin_valid,
                                     query_mock, admin_access_token, role_editor_valid, db_session):
        new_user_valid['role'] = role_editor_valid
        Role.query.filter_by.return_value.first.return_value = None

        _response = client.post(f'/api/users',
                                headers={'Authorization': f'Bearer {admin_access_token}'}, json=new_user_valid)
        assert _response.status_code == 400
        data = json.loads(_response.data.decode('utf-8'))
        assert data == 'Invalid role.'

    def test_add_user_permission_required(self, client, config_valid, login_valid_request, user_valid,
                      role_admin_valid,
                      user_access_token, query_mock):
        User.query.all.return_value = [login_valid_request]

        _response = client.post(f'/api/users', headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403
