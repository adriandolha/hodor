import requests
from requests.auth import HTTPBasicAuth

from hodor.auth import BearerTokenValidator
from hodor.serializers import to_json, from_json


class TestJWT:
    def test_register(self, config_valid, user_valid1):
        _response = requests.post(url=f'{config_valid["root_url"]}/api/auth/signup',
                                  headers={'Content-Type': 'application/json'}, timeout=5,
                                  data=to_json(user_valid1).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        print(_response_data)
        assert _response_data['access_token']
        assert _response_data['roles'] == ['ROLE_USER']

    def test_login_guest_user(self, config_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/signin',
                                 headers={'Content-Type': 'application/json'}, timeout=3,
                                 auth=HTTPBasicAuth(config_valid['guest_user'], config_valid['guest_password']))
        print(_response.content)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        print(_response_data)
        assert _response_data['access_token']
        assert _response_data['id']
        assert _response_data['roles'] == ['ROLE_USER']
        assert _response_data['email'] == 'guest@gmail.com'
        assert _response_data['username'] == 'guest'
        assert _response_data['permissions'] == ['books:add', 'books:read', 'books:write', 'users:profile']

    def test_login_admin_permissions(self, config_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/signin',
                                 headers={'Content-Type': 'application/json'}, timeout=3,
                                 auth=HTTPBasicAuth(config_valid['guest_user'], config_valid['guest_password']))
        print(_response.content)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        print(_response_data)
        assert _response_data['access_token']
        assert _response_data['id']
        assert _response_data['roles'] == ['ROLE_USER']
        assert _response_data['email'] == 'guest@gmail.com'
        assert _response_data['username'] == 'guest'
        assert _response_data['permissions'] == ['books:add', 'books:read', 'books:write', 'users:profile']

    def test_profile(self, config_valid, admin_access_token):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/profile',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=3)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        assert _response_data['username'] == 'admin'
        assert _response_data['roles'] == ['ROLE_ADMIN']

    def test_get_user(self, config_valid, admin_access_token):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/users/guest',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=3)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        assert _response_data['username'] == 'guest'

    def test_logout(self, config_valid, admin_access_token_logout):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/signout',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token_logout}'}, timeout=3)
        assert _response.status_code == 200
        assert from_json(_response.content.decode('utf-8')) == 'Logged out.'

    def test_jwk(self, config_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/.well-known/jwks.json',
                                 headers={'Content-Type': 'application/json'},
                                 timeout=3)
        assert _response.status_code == 200
        assert from_json(_response.content.decode('utf-8'))['keys']

    def test_health(self, config_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/health',
                                 timeout=3)
        assert _response.status_code == 200

    def test_bearer_token(self, config_valid, admin_access_token):
        access_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImRlbW9fa2V5IiwidHlwIjoiSldUIn0.eyJpc3MiOiJsb3JlbS5pcHN1bS5kZXYiLCJhdWQiOiJsb3JlbS5pcHN1bS5hdXRoIiwic3ViIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsInJvbGVzIjpbIlJPTEVfQURNSU4iXSwiZXhwIjoxNjQ0MDA0ODAwLCJpYXQiOjE2NDM5OTA0MDB9.Z0jcTu3a4OwMpf0nT4nrYHrNkV2Az1epwB6bIKIhXbH_2ke2hrgQsChevF_0MX_aYb7J8xv8cUJPO2xi7eOjbDukjQ3wvycnAS-Vb9xRknXSLB4lK6yTZtsCdaQ0_NUv4DYYjaflc9-JbFfNzmvxQua7N5f2_oVforlSFkhpPrquJjige7kRX4YY05bOkCCeZBbphaUyivigj2W-NbZ0v8QCZ9FfO9h9NCy_gHrUPQr3wpZR5TTkHrZMkutjNWsalo-rN98JsiXQfFBaJxyL5I7M4LoLXRHHRJ7tbiOxAtcevqcHMDXQpEIdvWPS7VSOyj32U7hxg7mGs4a7CVfjFO29ydBWhS_bsUQw1Z25bv3dV2lqPkRZfzB0VXyWdUHUjgfH4SjsV67xuIHlIrkX9VbhEb4K78d-r5TEpLCJnN7ZsPSA8DPW2XQd0TLKDoEjwH8CccQcFtEYwnNDxhI_ThtMxMG9a2FlEDdLKxW3O80iQ4CzRtDyJlhR4VhtPld901K_v3_tIgknodLzKnlmzbx11OX8pbnVU9NP_gqrnAjMnADp3XnGuYuq8iQTnC5t0g909F08KgH3Uz959bjGW6XfCC_dYBAmTeDhhsLKKK2XiMH5p-jzU0HgLjXdpkpALCNpX280fllVC2DP2puIIJJ0I3ed2JsUbYm3itN3jls'
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/profile',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {access_token}'}, timeout=3)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        assert _response_data['username'] == 'admin'
        assert _response_data['roles'] == ['ROLE_ADMIN']


class TestUser:
    def register_user(self, user: dict, admin_access_token, config_valid):
        username = user['username']
        _response = requests.delete(url=f'{config_valid["root_url"]}/api/users/{username}',
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': f'Bearer {admin_access_token}'}, timeout=3)
        assert _response.status_code == 204

        _response = requests.post(url=f'{config_valid["root_url"]}/api/auth/signup',
                                  headers={'Content-Type': 'application/json'}, timeout=5,
                                  data=to_json(user).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        headers = {'Authorization': f'Bearer {admin_access_token}'}
        _response = requests.get(url=f'{config_valid["root_url"]}/api/users/{username}',
                                 headers=headers, timeout=5,
                                 data=to_json(user).encode('utf-8'))
        assert _response.status_code == 200
        return from_json(_response.content.decode('utf-8'))

    def test_update_user(self, config_valid, user_valid2, role_editor_valid, admin_access_token):
        _user = self.register_user(user_valid2, admin_access_token, config_valid)
        username = user_valid2['username']
        headers = {'Authorization': f'Bearer {admin_access_token}'}

        _user['role'] = role_editor_valid
        _response = requests.put(url=f'{config_valid["root_url"]}/api/users/{username}',
                                 headers=headers, timeout=5,
                                 data=to_json(_user).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        _updated_user = from_json(_response.content.decode('utf-8'))
        print(_updated_user)
        assert _updated_user['role']['name'] == role_editor_valid['name']
        assert _updated_user['role']['default'] == role_editor_valid['default']
        for perm in _updated_user['role']['permissions']:
            assert perm in role_editor_valid['permissions']

    def test_get_users(self, config_valid, admin_access_token):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/users',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=3)
        assert _response.status_code == 200
        _response_data = from_json(_response.content.decode('utf-8'))
        assert _response_data['total'] > 1
        assert len(_response_data['items']) > 1
        assert _response_data['items'][0].get('username')
        assert _response_data['items'][0].get('role')

    def test_add_user_valid(self, config_valid, new_user_valid, role_editor_valid, admin_access_token):
        username = new_user_valid['username']
        headers = {'Authorization': f'Bearer {admin_access_token}'}
        _response = requests.delete(url=f'{config_valid["root_url"]}/api/users/{username}',
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': f'Bearer {admin_access_token}'}, timeout=3)
        assert _response.status_code == 204

        new_user_valid['role'] = role_editor_valid
        _response = requests.post(url=f'{config_valid["root_url"]}/api/users',
                                  headers=headers, timeout=5,
                                  data=to_json(new_user_valid).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        _updated_user = from_json(_response.content.decode('utf-8'))
        print(_updated_user)
        assert _updated_user['username'] == new_user_valid['username']
        assert _updated_user['email'] == new_user_valid['email']
        assert _updated_user['login_type'] == 'basic'
        assert not _updated_user.get('password')
        assert not _updated_user.get('password_hash')
        assert _updated_user['role']['name'] == role_editor_valid['name']
        assert _updated_user['role']['default'] == role_editor_valid['default']
        for perm in _updated_user['role']['permissions']:
            assert perm in role_editor_valid['permissions']
