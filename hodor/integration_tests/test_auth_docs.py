import requests

from hodor.serializers import to_json, from_json


class TestRole:
    def assert_route_decorators_preserve_openapi_docs(self, spec):
        assert spec['paths']['/api/auth/roles']['post']

    def test_docs(self, config_valid, admin_access_token, role_editor_valid):
        _response = requests.get(url=f'{config_valid["root_url"]}/api/auth/spec',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                 data=to_json(role_editor_valid).encode('utf-8'))
        assert _response.status_code == 200
        data = from_json(_response.content.decode('utf-8'))
        self.assert_route_decorators_preserve_openapi_docs(data)
        print(data)
