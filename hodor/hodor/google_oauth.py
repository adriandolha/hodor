import logging

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, url_for, g, redirect, request, flash, jsonify, session
from flask import current_app as app

from hodor import AppContext, db
from hodor.auth import issue_token_for_user
from hodor.models import User, Role, LoginType

google_oauth = Blueprint('google_oauth', __name__)
LOGGER = logging.getLogger('lorem-ipsum')


def app_context():
    if 'app_context' not in g:
        g.app_context = AppContext.local_context()

    return g.app_context


oauth = OAuth(app)


@google_oauth.route('/')
def google():
    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For developement purpose you can directly put it
    # here inside double quotes
    configure_oauth()

    # Redirect to google_auth function
    # redirect_uri = url_for('google_oauth.google_auth', _external=True)
    redirect_uri = 'http://localhost:8081/login'
    return oauth.google.authorize_redirect(f'{redirect_uri}')


def configure_oauth():
    _app_context = app_context()
    GOOGLE_CLIENT_ID = _app_context.config.get('google_client_id')
    GOOGLE_CLIENT_SECRET = _app_context.config.get('google_client_secret')
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile',
            'redirect_uri': 'http://localhost:8081/login'
        }
    )


@google_oauth.route('/login')
def google_login():
    """
        Initiate google authorization code oauth.
        ---
        responses:
                200:
                    description: Redirect to google oauth.

    """
    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For developement purpose you can directly put it
    # here inside double quotes
    _app_context = app_context()
    GOOGLE_CLIENT_ID = _app_context.config.get('google_client_id')
    redirect_url = url_for('google_oauth.google', scope='profile', response_type='code', client_id=GOOGLE_CLIENT_ID)
    LOGGER.debug(redirect_url)
    return redirect(redirect_url)


@google_oauth.route('/auth/')
def google_auth():
    """
        Redirect uri after google authorization code oauth. Authenticates user using google information, login_type
        set to google.
        ---
        responses:
                200:
                    description: Redirect to home page.
                401:
                    description: Authentication issue.
    """

    _token = oauth.google.authorize_access_token()
    google_user = oauth.google.parse_id_token(_token)
    LOGGER.debug(f" Google User {google_user}")
    username = google_user['name'].replace(' ', '').lower()
    LOGGER.debug(f" Google User Name {username}")
    user = User.query.filter_by(email=google_user['email']).first()
    _password = "google"
    if not user:
        user = User(email=google_user['email'],
                    username=username,
                    password=_password,
                    login_type=LoginType.GOOGLE)
        db.session.add(user)
        db.session.commit()
    if user is not None and user.verify_password(_password):
        # login_user(user, remember=False)
        next = request.args.get('next')
        if next is None or not next.startswith('/'):
            next = url_for('main.index')
        return redirect(next)
    flash('Invalid username or password.')

    return redirect(url_for('main.index'))


@google_oauth.route('/token')
def token():
    configure_oauth()
    state = request.args['state']
    LOGGER.debug(f"State [{state}], _google_authlib_state_[{session.get('_google_authlib_state_')}]")
    LOGGER.debug(session)
    session['_google_authlib_state_'] = state
    _token = oauth.google.authorize_access_token()
    google_user = oauth.google.parse_id_token(_token)
    LOGGER.debug(f" Google User {google_user}")
    username = google_user['name'].replace(' ', '').lower()
    LOGGER.debug(f" Google User Name {username}")
    user = User.query.filter_by(email=google_user['email']).first()
    _password = "google"
    if not user:
        user = User.query.filter_by(username=username).first()
        if user:
            LOGGER.debug(f" Username {username} already exists. Using email as username.")
            username = google_user['email']
        user = User(email=google_user['email'],
                    username=username,
                    password=_password,
                    login_type=LoginType.GOOGLE)
        db.session.add(user)
        db.session.commit()
    access_token = issue_token_for_user(user)
    LOGGER.debug(f'Access token {access_token}')

    return jsonify({**user.to_json(), 'access_token': access_token}), 200


@google_oauth.after_request
def apply_cors(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    return response
