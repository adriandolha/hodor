import json
import os

from hodor.models import Role

os.environ['env'] = 'test'


class TestAuthRole:
    def test_role_delete(self, client, config_valid, role_add_valid_request, user_admin_valid, role_editor_valid,
                         query_mock, admin_access_token):
        _response = client.delete(f'/api/auth/roles/{role_editor_valid["name"]}',
                                  headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 204

    def test_role_get(self, client, config_valid, role_get_valid_request, user_admin_valid, role_editor_valid,
                      query_mock, admin_access_token):
        _response = client.get(f'/api/auth/roles/{role_editor_valid["name"]}',
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))

        assert data['name'] == role_editor_valid['name']
        assert len(data['permissions']) == 4
        assert data['permissions'] == role_editor_valid['permissions']

    def test_get_roles(self, client, config_valid, role_get_valid_request, user_admin_valid, role_editor_valid,
                       query_mock, admin_access_token):
        from hodor.models import Role
        Role.query.all.return_value = [role_get_valid_request]
        _response = client.get(f'/api/auth/roles',
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        assert data['total'] == 1
        assert data['total'] == len(data['items'])
        _role = data['items'][0]
        assert _role['name'] == role_editor_valid['name']
        assert len(_role['permissions']) == 4
        assert _role['permissions'] == role_editor_valid['permissions']

    def test_role_get_permission_required(self, client, config_valid, role_add_existing_request, user_admin_valid,
                                          role_editor_valid, user_access_token,
                                          query_mock):
        _response = client.get(f'/api/auth/roles/fake', json=role_editor_valid,
                               headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_role_add(self, client, config_valid, role_add_valid_request, admin_access_token, role_editor_valid):
        _response = client.post('/api/auth/roles', json=role_editor_valid,
                                headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        print(data)
        assert data['name'] == role_editor_valid['name']
        assert len(data['permissions']) == 4
        assert data['permissions'] == role_editor_valid['permissions']

    def test_role_update(self, client, config_valid, role_update_valid_request, admin_access_token, role_editor_valid):
        role_name = role_editor_valid['name']
        _response = client.put(f'/api/auth/roles/{role_name}', json=role_editor_valid,
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        data = json.loads(_response.data.decode('utf-8'))
        print(data)
        assert _response.status_code == 200
        assert data['name'] == role_editor_valid['name']
        assert len(data['permissions']) == 4
        assert data['permissions'] == role_editor_valid['permissions']

    def test_role_update_invalid_role_name(self, client, config_valid, role_update_valid_request, admin_access_token,
                                           role_editor_valid):
        role_name = 'bla'
        _response = client.put(f'/api/auth/roles/{role_name}', json=role_editor_valid,
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        data = json.loads(_response.data.decode('utf-8'))
        print(data)
        assert _response.status_code == 400
        assert data == 'Invalid role name.'

    def test_role_update_not_found(self, client, config_valid, role_add_valid_request, admin_access_token,
                                   role_editor_valid):
        role_name = role_editor_valid['name']
        Role.query.filter_by.return_value.first.return_value = None
        _response = client.put(f'/api/auth/roles/{role_name}', json=role_editor_valid,
                               headers={'Authorization': f'Bearer {admin_access_token}'})
        data = json.loads(_response.data.decode('utf-8'))
        print(data)
        assert _response.status_code == 404
        assert data == 'Role not found.'

    def test_role_add_existing(self, client, config_valid, role_add_existing_request, user_admin_valid,
                               role_editor_valid,
                               query_mock, admin_access_token):
        _response = client.post('/api/auth/roles', json=role_editor_valid,
                                headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 400
        data = json.loads(_response.data.decode('utf-8'))
        assert data == 'Role already exists.'

    def test_role_add_permission_required(self, client, config_valid, role_add_existing_request, user_admin_valid,
                                          role_editor_valid, user_access_token,
                                          query_mock):
        _response = client.post('/api/auth/roles', json=role_editor_valid,
                                headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_role_update_permission_required(self, client, config_valid, role_update_valid_request, user_admin_valid,
                                             role_editor_valid, user_access_token,
                                             query_mock):
        _response = client.put(f'/api/auth/roles/bla', json=role_editor_valid,
                               headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_role_delete_permission_required(self, client, config_valid, role_add_existing_request, user_admin_valid,
                                             role_editor_valid, user_access_token,
                                             query_mock):
        _response = client.delete(f'/api/auth/roles/fake', json=role_editor_valid,
                                  headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_get_roles_permission_required(self, client, config_valid, role_add_existing_request, user_admin_valid,
                                           role_editor_valid, user_access_token,
                                           query_mock):
        _response = client.get(f'/api/auth/roles', json=role_editor_valid,
                               headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403
