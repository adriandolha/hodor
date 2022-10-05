import requests

from hodor.serializers import to_json, from_json


class TestPermission:
    def test_permission_add(self, config_valid, admin_access_token, permission_edit_books_valid):
        _response = requests.delete(
            url=f'{config_valid["root_url"]}/api/auth/permissions/{permission_edit_books_valid["name"]}',
            headers={'Content-Type': 'application/json',
                     'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
            data=to_json(permission_edit_books_valid).encode('utf-8'))
        assert _response.status_code == 204
        _response = requests.post(url=f'{config_valid["root_url"]}/api/auth/permissions',
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                  data=to_json(permission_edit_books_valid).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        data = from_json(_response.content.decode('utf-8'))
        assert data['name'] == permission_edit_books_valid['name']
        assert data['id'] == permission_edit_books_valid['id']

    def test_get_permissions(self, config_valid, admin_access_token):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/permissions',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=5)
        assert _response.status_code == 200
        data = from_json(_response.content.decode('utf-8'))
        assert data['total'] > 1
        assert data['total'] == len(data['items'])
        _perm = data['items'][0]
        assert _perm.get('name')
        assert _perm.get('id')