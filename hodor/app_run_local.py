import os

if __name__ == "__main__" or __name__ == 'app' and os.getenv('env') != 'test':
    import json

    print('Running local app...')
    with open(f"{os.path.expanduser('~')}/.cloud-projects/hodor-local.json", "r") as _file:
        json = dict(json.load(_file))
        print(json)
        for k, v in json.items():
            os.environ[k] = str(v)
    import app

    app.create_flask_app().run(port=5000, debug=True)
