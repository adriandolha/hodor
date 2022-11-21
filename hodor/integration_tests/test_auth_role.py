import requests

from hodor.serializers import to_json, from_json


class TestRole:
    def test_role_add(self, config_valid, admin_access_token, role_editor_valid):
        _response = requests.delete(url=f'{config_valid["root_url"]}/api/roles/{role_editor_valid["name"]}',
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                    data=to_json(role_editor_valid).encode('utf-8'))
        assert _response.status_code == 204
        _response = requests.post(url=f'{config_valid["root_url"]}/api/roles',
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                  data=to_json(role_editor_valid).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        data = from_json(_response.content.decode('utf-8'))
        assert data['name'] == role_editor_valid['name']
        assert len(data['permissions']) == 4
        for perm in data['permissions']:
            assert perm in role_editor_valid['permissions']

    def test_role_update(self, config_valid, admin_access_token, role_update_valid):
        _response = requests.delete(url=f'{config_valid["root_url"]}/api/roles/{role_update_valid["name"]}',
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                    data=to_json(role_update_valid).encode('utf-8'))
        assert _response.status_code == 204
        _response = requests.post(url=f'{config_valid["root_url"]}/api/roles',
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                  data=to_json(role_update_valid).encode('utf-8'))
        print(_response.content)
        assert _response.status_code == 200
        role_update_valid['permissions'] = [{'id': 'books:read', 'name': 'books:read'}]
        _response = requests.put(url=f'{config_valid["root_url"]}/api/roles/{role_update_valid["name"]}',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                 data=to_json(role_update_valid).encode('utf-8'))
        data = from_json(_response.content.decode('utf-8'))
        assert len(data['permissions']) == 1
        assert data['permissions'] == [{'id': 'books:read', 'name': 'books:read'}]

    def test_role_get(self, config_valid, admin_access_token, role_admin_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/roles/{role_admin_valid["name"]}',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=5)
        assert _response.status_code == 200
        data = from_json(_response.content.decode('utf-8'))
        assert data['name'] == role_admin_valid['name']
        assert len(data['permissions']) == 5
        assert data['permissions'] == role_admin_valid['permissions']

    def test_get_roles(self, config_valid, admin_access_token, role_admin_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/roles',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=5)
        assert _response.status_code == 200
        data = from_json(_response.content.decode('utf-8'))
        assert data['total'] > 1
        assert data['total'] == len(data['items'])
        _role = data['items'][0]
        assert _role.get('name')
        assert _role.get('permissions')
