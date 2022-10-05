import json
import os

os.environ['env'] = 'test'


class TestAuthPermission:
    def test_permission_delete(self, client, config_valid, user_admin_valid, role_editor_valid,
                               query_mock, admin_access_token):
        _response = client.delete(f'/api/auth/permissions/{role_editor_valid["name"]}',
                                  headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 204

    def test_permission_add(self, client, config_valid, permission_add_valid_request, admin_access_token,
                            permission_edit_books_valid):
        from hodor.models import Permission
        Permission.query.filter_by.return_value.first.return_value = None
        _response = client.post('/api/auth/permissions', json=permission_edit_books_valid,
                                headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        print(data)
        assert data['name'] == permission_edit_books_valid['name']
        assert data['id'] == permission_edit_books_valid['id']

    def test_permission_add_existing(self, client, config_valid, user_admin_valid,
                                     role_editor_valid,
                                     query_mock, admin_access_token):
        _response = client.post('/api/auth/permissions', json=role_editor_valid,
                                headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 400
        data = json.loads(_response.data.decode('utf-8'))
        assert data == 'Permission already exists.'

    def test_permission_add_permission_required(self, client, config_valid, role_add_existing_request, user_admin_valid,
                                                role_editor_valid, user_access_token,
                                                query_mock):
        _response = client.post('/api/auth/permissions', json=role_editor_valid,
                                headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_permission_delete_permission_required(self, client, config_valid, user_admin_valid, role_editor_valid,
                                                   user_access_token,
                                                   query_mock):
        _response = client.delete(f'/api/auth/permissions/fake', json=role_editor_valid,
                                  headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403

    def test_get_permissions(self, client, config_valid, permission_add_valid_request, admin_access_token,
                             permission_edit_books_valid):
        from hodor.models import Permission
        Permission.query.filter_by.return_value.first.return_value = None
        Permission.query.all.return_value = [Permission.from_str(permission_edit_books_valid['name'])]
        _response = client.get('/api/auth/permissions', headers={'Authorization': f'Bearer {admin_access_token}'})
        assert _response.status_code == 200
        data = json.loads(_response.data.decode('utf-8'))
        assert data['total'] == 1
        _perm = data['items'][0]
        assert _perm['name'] == permission_edit_books_valid['name']
        assert _perm['id'] == permission_edit_books_valid['id']

    def test_get_permissions_requires_permission(self, client, config_valid, permission_add_valid_request,
                                                 user_access_token,
                                                 permission_edit_books_valid):
        _response = client.get('/api/auth/permissions', headers={'Authorization': f'Bearer {user_access_token}'})
        assert _response.status_code == 403
