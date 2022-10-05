import os

from hodor.app import create_flask_app

if __name__ == "__main__" or __name__ == 'app' and os.getenv('env') != 'test':
    app = create_flask_app()
