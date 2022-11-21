import datetime
import json
import os

os.environ['env'] = 'test'


class TestAuthToken:
    def issue_token(self, user: dict, role: dict) -> str:
        from hodor.models import User, Permission, Role
        from hodor.auth import issue_token_for_user
        role = Role(id=user['id'], name=role['name'],
                    permissions=[Permission.from_str(perm) for perm in role['permissions']])
        Role.query.filter_by.return_value.first.return_value = role
        user = User.from_dict(user)
        user.role = role
        User.query.filter_by.return_value.filter_by.return_value.first.return_value = user
        User.query.filter_by.return_value.first.return_value = user
        return issue_token_for_user(user)

    def test_auth_token_permissions_valid(self, client, query_mock, user_admin_valid, role_admin_valid):
        _response = client.get('/api/profile', headers={
            'Authorization': f'Bearer {self.issue_token(user_admin_valid, role_admin_valid)}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        assert data['username'] == user_admin_valid['username']
        assert len(data['roles']) == 1
        assert role_admin_valid['name'] in data['roles']

    def test_auth_token_permissions_missing(self, client, query_mock, user_valid, role_user_valid):
        _response = client.get('/api/users/admin', headers={
            'Authorization': f'Bearer {self.issue_token(user_valid, role_user_valid)}'})
        assert _response.status_code == 403
        assert json.loads(_response.data.decode('utf-8')) == 'Forbidden.'

    def test_auth_token_sub_missing(self, client, login_valid_request, user_valid, role_user_valid):
        from hodor.auth import new_token
        _token = new_token({
            "iss": "lorem.ipsum.dev",
            "aud": "lorem.ipsum.auth",
            "email": user_valid['email'],
            "roles": [
                role_user_valid['name']
            ],
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=4),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc)
        })
        _response = client.get('/api/users/admin', headers={
            'Authorization': f'Bearer {_token}'})
        assert _response.status_code == 403
        assert json.loads(_response.data.decode('utf-8')) == 'Forbidden.'

    def test_auth_token_user_not_found(self, client, query_mock, user_valid, role_user_valid):
        from hodor.models import User

        _token = self.issue_token(user_valid, role_user_valid)
        User.query.filter_by.return_value.filter_by.return_value.first.return_value = None
        User.query.filter_by.return_value.first.return_value = None
        _response = client.get('/api/profile', headers={
            'Authorization': f'Bearer {_token}'})
        assert _response.status_code == 403
        assert json.loads(_response.data.decode('utf-8')) == 'Forbidden.'

    def test_auth_token_missing(self, client, query_mock, user_valid, role_user_valid):
        _response = client.get('/api/profile')
        assert _response.status_code == 401
        assert json.loads(_response.data.decode('utf-8')) == 'Invalid token.'

    def test_auth_token_authorization_header_invalid(self, client, query_mock, user_valid, role_user_valid):
        from hodor.models import User

        _token = self.issue_token(user_valid, role_user_valid)
        User.query.filter_by.return_value.filter_by.return_value.first.return_value = None
        User.query.filter_by.return_value.first.return_value = None
        _response = client.get('/api/profile', headers={
            'Authorization': f'Beare {_token}'})
        assert _response.status_code == 401
        assert json.loads(_response.data.decode('utf-8')) == 'Invalid token.'

    def test_auth_token_blacklisted(self, client, query_mock, user_valid, role_user_valid):
        from hodor.models import BlacklistToken
        _token = self.issue_token(user_valid, role_user_valid)
        BlacklistToken.query.filter_by.return_value.first.return_value = BlacklistToken(token=_token)
        _response = client.get('/api/profile', headers={
            'Authorization': f'Bearer {_token}'})
        assert _response.status_code == 401
        assert json.loads(_response.data.decode('utf-8')) == 'Invalid token.'

    def test_auth_token_skip_permissions_check_when_head_or_options(self, client, query_mock, user_valid,
                                                                    role_user_valid):
        _response = client.head('/api/users/admin', headers={
            'Authorization': f'Bearer {self.issue_token(user_valid, role_user_valid)}'})
        assert _response.status_code == 200
        _response = client.options('/api/users/admin', headers={
            'Authorization': f'Bearer {self.issue_token(user_valid, role_user_valid)}'})
        assert _response.status_code == 200
