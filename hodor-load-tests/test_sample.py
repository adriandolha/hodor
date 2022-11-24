import json
import os
import secrets
from functools import lru_cache

from locust import FastHttpUser, task, between

API_URL = os.getenv('root_url', 'http://ecs-load-balancer-850455720.eu-central-1.elb.amazonaws.com')


def get_access_token(client, username, password):
    _response = client.get(url=f'{API_URL}/api/signin',
                           headers={'Content-Type': 'application/json'}, timeout=3,
                           auth=(username, password))
    # print(_response.content)
    _response_data = json.loads(_response.content.decode('utf-8'))
    # print(_response_data)
    access_token_ = _response_data['access_token']
    return access_token_


@lru_cache
def load_config():
    import json
    print('Load config...')
    with open(f"{os.path.expanduser('~')}/.cloud-projects/hodor-load-tests.json", "r") as _file:
        json = dict(json.load(_file))
        print(json)
        for k, v in json.items():
            os.environ[k] = str(v)
        os.environ['db_setup'] = 'False'
        return os.environ


class TestSample(FastHttpUser):
    wait_time = between(3, 10)

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.client.verify = False
        load_config()
        print('Starting tests...')
        admin_access_token = get_access_token(self.client, os.environ['admin_user'], os.environ['admin_password'])
        _response = self.client.get(f'{API_URL}/api/users',
                                    headers={'Authorization': f'Bearer {admin_access_token}'})
        data = json.loads(_response.content.decode('utf-8'))
        print(data)

        for item in data['items']:
            username_ = item['username']
            print(username_)
        for user_index in range(1, 500):
            new_username = f'test_user{user_index}'
            new_password = secrets.token_urlsafe(16)
            if not any([item['username'] == new_username for item in data['items']]):

                new_user = {
                    'username': new_username,
                    'email': f'{new_username}@hodor.com',
                    'password': new_password,
                    'role': {'name': 'ROLE_USER'}
                }
                _response = self.client.post(url=f'{API_URL}/api/users',
                                             headers={'Authorization': f'Bearer {admin_access_token}'}, timeout=5,
                                             data=json.dumps(new_user).encode('utf-8'))
                if _response.status_code == 200:
                    print(f'Created user {new_user}...')
                    self.username = new_username
                    self.password = new_password
                    break
                else:
                    print(f'Failed to create user {new_user}...')
                    print(_response.content)

    @task(1)
    def signin(self):
        self.client.get(f'{API_URL}/api/profile',
                        headers={
                            'Authorization': f'Bearer {get_access_token(self.client, self.username, self.password)}'})
