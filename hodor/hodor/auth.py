from functools import lru_cache

import datetime
import logging

from authlib.jose import JsonWebKey, jwt
from flask import g, jsonify, Blueprint, request, current_app as app, make_response
from sqlalchemy import or_

from hodor import db, create_app_context, api
from hodor.models import LoginType, User, Permission, BlacklistToken, Permissions, Role, ValidationError
from hodor.serializers import from_json, to_json
from flask_swagger import swagger

LOGGER = logging.getLogger('lorem-ipsum-auth')
token_auth = Blueprint('token_auth', __name__)
users = Blueprint('users', __name__)


def app_context():
    if 'app_context' not in g:
        g.app_context = create_app_context()
    return g.app_context


def new_token(payload: dict):
    key = jwk_key()
    header = {'alg': 'RS256', 'kid': 'demo_key'}
    token = jwt.encode(header, payload, key)
    LOGGER.debug(token)
    return token.decode('utf-8')


@lru_cache()
def jwk_key():
    with open(app_context().config['jwk_private_key_path'], 'rb') as f:
        key = JsonWebKey.import_key(f.read())
    return key


def issue_token_for_user(user: User):
    access_token = new_token({
        "iss": "lorem.ipsum.dev",
        "aud": "lorem.ipsum.auth",
        "sub": user.username,
        "email": user.email,
        "roles": [
            user.role.name
        ],
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=4),
        "iat": datetime.datetime.now(tz=datetime.timezone.utc)
    })
    return access_token


class AuthenticationError(ValueError):
    pass


class AuthorizationError(ValueError):
    pass


class BearerTokenValidator:
    def __init__(self, access_token):
        self.access_token = access_token
        user_service = app_context().user_service
        self.payload = user_service.decode_auth_token(access_token, get_jwk())

    def check_is_blacklisted(self):
        is_blacklisted_token = BlacklistToken.check_blacklist(self.access_token)
        if is_blacklisted_token:
            LOGGER.debug('Token blacklisted.')
            raise AuthenticationError('Invalid token.')
        return self

    def check_username_claim(self):
        if not self.payload.get('sub'):
            LOGGER.debug('Token missing sub.')
            raise AuthorizationError('Forbidden.')
        return self

    def check_user_exists(self, user):
        if not user:
            LOGGER.debug('Token user not found.')
            raise AuthorizationError('Forbidden.')
        return self

    def check_has_permissions(self, user: User, permissions: list):
        has_permissions = True
        for permission in permissions:
            if not user.role.has_permission(Permission.from_enum(permission)):
                LOGGER.debug(f'Missing permission {permission}.')
                has_permissions = False
        LOGGER.debug(f'Required permissions: {permissions}')
        if not has_permissions:
            raise AuthorizationError('Forbidden.')
        return self

    @staticmethod
    def from_authorization_header(authorization_header: str):
        if not authorization_header:
            LOGGER.debug('Authorization header not found.')
            raise AuthenticationError('Invalid token.')
        if 'Bearer ' not in authorization_header:
            LOGGER.debug('Bearer token not found.')
            raise AuthenticationError('Invalid token.')
        access_token = authorization_header.split('Bearer')[1].strip()
        LOGGER.debug(f'Bearer token is:\n"{access_token}"')
        return BearerTokenValidator(access_token)


def should_skip_auth(flask_request):
    """
    Return true if should skip auth, e.g. when method is OPTIONS like when performing a React request.
    :param flask_request: Flask request.
    :return:
    """
    return flask_request.method in ['HEAD', 'OPTIONS']


def requires_permission(permissions: list):
    def requires_permission_decorator(function):
        def wrapper(*args, **kwargs):
            LOGGER.info(f'Authorization...\n{request.headers}')
            if should_skip_auth(request):
                return jsonify('ok')
            authorization_header = request.headers.get('Authorization')
            bearer_token_validator = BearerTokenValidator.from_authorization_header(authorization_header) \
                .check_is_blacklisted() \
                .check_username_claim()
            user = User.query.filter_by(username=bearer_token_validator.payload['sub']).first()

            bearer_token_validator.check_user_exists(user) \
                .check_has_permissions(user, permissions)
            g.access_token = bearer_token_validator.access_token
            g.user = user

            _result = function(*args, **kwargs)
            return _result

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return requires_permission_decorator


class ExceptionHandlers:
    def __init__(self, app):
        @app.errorhandler(AuthorizationError)
        def handle_authorization_exception(e):
            """Return403 forbidden."""
            return jsonify(str(e)), 403

        @app.errorhandler(AuthenticationError)
        def handle_authentication_exception(e):
            """Return401 authentication error."""
            return jsonify(str(e)), 401

        @app.errorhandler(ValidationError)
        def handle_authentication_exception(e):
            """Return401 authentication error."""
            return jsonify(str(e)), 400


@token_auth.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Lorem Ipsum Authentication"
    return jsonify(swag)


@token_auth.route('/signin', methods=['GET', 'POST'])
def login():
    """
        Signin by POST credentials or UsernamePassword GET.
        ---
        definitions:
          - schema:
              id: UsernamePassword
              properties:
                username:
                 type: string
                 description: username
                password:
                  type: string
                  description: password
          - schema:
              id: User
              properties:
                id:
                 type: string
                 description: user id
                username:
                 type: string
                 description: username
                email:
                 type: string
                 description: email
                login_type:
                 type: string
                 description: Login type (e.g. google)
                roles:
                 type: array
                 description: List of user roles.
                 items:
                   type: string
          - schema:
              id: LoginResponse
              allOf:
              - $ref: "#/definitions/User"
              properties:
                accessToken:
                  type: string
                  description: access token, JWT format
        parameters:
            - in: body
              name: loginRequest
              required: true
              description: username and password
              schema:
                  $ref: "#/definitions/UsernamePassword"
        responses:
                200:
                    description: User profile including access token.
                    schema:
                        $ref: '#/definitions/LoginResponse'
                401:
                    description: Invalid username or password.
    """

    if request.method == 'POST':
        _request = from_json(request.data.decode('utf-8'))
        username = _request['username']
        password = _request['password']
    else:
        username = request.authorization.username
        password = request.authorization.password

    user = User.query.filter_by(username=username).filter_by(
        login_type=LoginType.BASIC).first()
    if user is None or not user.verify_password(password):
        return jsonify('Invalid username or password'), 401
    access_token = issue_token_for_user(user)
    LOGGER.debug(f'Access token {access_token}')
    return jsonify({**user.to_json(), 'access_token': access_token}), 200


@token_auth.route('/signout', methods=['GET'])
@requires_permission([])
def logout():
    """
        Logout.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                200:
                    description: Logged out.
                    schema:
                        $ref: '#/definitions/LoginResponse'
                401:
                    description: Invalid token.
    """
    if not BlacklistToken.query.filter_by(token=g.access_token).first():
        blacklist_token = BlacklistToken(token=g.access_token)
        db.session.add(blacklist_token)
        db.session.commit()
    return jsonify('Logged out.'), 200


@token_auth.route('/signup', methods=['POST'])
def register():
    """
        Signin by POST credentials or UsernamePassword GET.
        ---
        definitions:
          - schema:
              id: RegisterRequest
              properties:
                username:
                 type: string
                 description: username
                password:
                  type: string
                  description: password
                email:
                  type: string
                  description: email

        parameters:
            - in: body
              name: registerRequest
              required: true
              description: username and password
              schema:
                  $ref: "#/definitions/RegisterRequest"
        responses:
                200:
                    description: User profile including access token.
                    schema:
                        $ref: '#/definitions/LoginResponse'
                401:
                    description: Invalid username or password.
    """

    _request = from_json(request.data.decode('utf-8'))
    if User.query.filter_by(username=_request['username']).first():
        return jsonify('User already registered'), 400
    user = User(email=_request['email'],
                username=_request['username'],
                password=_request['password'])
    default_role = Role.query.filter_by(default=True).first()
    if not default_role:
        raise ValidationError('Invalid role.')
    user.role = default_role

    db.session.add(user)
    db.session.commit()
    access_token = issue_token_for_user(user)
    return jsonify({**user.to_json(), 'access_token': access_token}), 200


@token_auth.route('/profile', methods=['GET'])
@requires_permission([Permissions.USERS_PROFILE])
def profile():
    """
        Get user profile.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                200:
                    description: User profile.
                    schema:
                        $ref: '#/definitions/User'
                401:
                    description: Invalid token.
    """

    user = g.user
    return jsonify(user.to_json()), 200


@lru_cache()
def get_jwk():
    LOGGER.debug('Loading jwk from public key...')
    key_data = None
    with open(app_context().config['jwk_public_key_path'], 'rb') as _key_file:
        key_data = _key_file.read()
    LOGGER.debug(key_data)
    key = JsonWebKey.import_key(key_data, {'kty': 'RSA'})
    return {'keys': [{**key.as_dict(), 'kid': 'demo_key'}]}


@token_auth.route('/.well-known/jwks.json', methods=['GET'])
def jwk():
    """
        Get JWK.
        ---
        responses:
                200:
                    description: Return JWK.
    """

    LOGGER.debug('JWK...')
    key = get_jwk()
    LOGGER.debug(key)
    LOGGER.debug(key)
    return jsonify(key)


@users.route('/<username>', methods=['DELETE'])
@requires_permission([Permissions.USERS_ADMIN])
def delete_user(username):
    """
        Delete user.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                204:
                    description: User deleted.
                401:
                    description: Invalid token.
    """

    LOGGER.info('Delete user...')
    user = User.query.filter_by(username=username).first()
    if user:
        User.query.filter_by(username=username).delete()
    db.session.commit()
    return '', 204


@token_auth.route('/roles/<name>', methods=['DELETE'])
@requires_permission([Permissions.USERS_ADMIN])
def delete_role(name):
    """
        Delete user.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                204:
                    description: User deleted.
                401:
                    description: Invalid token.
    """

    LOGGER.info('Delete user...')
    role = Role.query.filter_by(name=name).first()
    if role:
        db.session.delete(role)
        db.session.commit()
    return '', 204


@token_auth.route('/permissions/<name>', methods=['DELETE'])
@requires_permission([Permissions.USERS_ADMIN])
def delete_permission(name):
    """
        Delete permission.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                204:
                    description: Permission deleted.
                401:
                    description: Authentication error.
                401:
                    description: Authorization error.
    """

    permission = Permission.query.filter_by(name=name).first()
    if permission:
        db.session.delete(permission)
        db.session.commit()
    return '', 204


@users.route('/<username>', methods=['GET'])
@requires_permission([Permissions.USERS_ADMIN])
def get_user(username):
    """
        Get user.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
            - in: query
              name: username
              required: true
              type: string
              description: username
        responses:
                200:
                    description: User profile.
                    schema:
                        $ref: '#/definitions/User'
                401:
                    description: Invalid token.
    """

    LOGGER.info('Get user...')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify('Not found.'), 404
    return jsonify(api.User.from_orm(user).dict()), 200


@users.route('/', methods=['GET'], strict_slashes=False)
@requires_permission([Permissions.USERS_ADMIN])
def get_users():
    """
        Get users.
        ---
        definitions:
          - schema:
              id: GetUsersResult
              type: object
              properties:
                total:
                  type: integer
                  description: Total number of items.
                items:
                  type: array
                  description: List of users
                  items:
                    oneOf:
                      - $ref: "#/definitions/User"
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                200:
                    description: List of users.
                    schema:
                        $ref: '#/definitions/GetUsersResult'
                401:
                    description: Invalid token.
    """

    _users = list(map(lambda user: api.User.from_orm(user).dict(), User.get_all()))
    return jsonify({'total': len(_users), 'items': _users}), 200


@token_auth.route('/roles', methods=['GET'], strict_slashes=False)
@requires_permission([Permissions.USERS_ADMIN])
def get_roles():
    """
        Get roles.
        ---
        definitions:
          - schema:
              id: GetRolesResult
              type: object
              properties:
                total:
                  type: integer
                  description: Total number of items.
                items:
                  type: array
                  description: List of roles
                  items:
                    oneOf:
                      - $ref: "#/definitions/Role"
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                200:
                    description: List of roles.
                    schema:
                        $ref: '#/definitions/GetRolesResult'
                401:
                    description: Invalid token.
    """

    _roles = list(map(lambda user: api.Role.from_orm(user).dict(), Role.query.all()))
    return jsonify({'total': len(_roles), 'items': _roles}), 200


@token_auth.route('/permissions', methods=['GET'], strict_slashes=False)
@requires_permission([Permissions.USERS_ADMIN])
def get_permissions():
    """
        Get permissions.
        ---
        definitions:
          - schema:
              id: GetPermissionsResult
              type: object
              properties:
                total:
                  type: integer
                  description: Total number of items.
                items:
                  type: array
                  description: List of permissions
                  items:
                    oneOf:
                      - $ref: "#/definitions/Permission"
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
        responses:
                200:
                    description: List of permissions.
                    schema:
                        $ref: '#/definitions/GetPermissionsResult'
                401:
                    description: Invalid token.
    """

    _permissions = list(map(lambda user: api.Permission.from_orm(user).dict(), Permission.query.all()))
    return jsonify({'total': len(_permissions), 'items': _permissions}), 200


@token_auth.route('/roles/<name>', methods=['GET'])
@requires_permission([Permissions.USERS_ADMIN])
def get_role(name):
    """
        Get role.
        ---
        parameters:
            - in: header
              name: X-Token-String
              required: true
              type: string
              description: Access token JWT.
            - in: query
              name: name
              required: true
              type: string
              description: Role name
        responses:
                200:
                    description: Role.
                    schema:
                        $ref: '#/definitions/User'
                401:
                    description: Invalid token.
    """

    role = Role.query.filter_by(name=name).first()
    if not role:
        return jsonify('Not found.'), 404
    return jsonify(api.Role.from_orm(role).dict()), 200


@token_auth.route('/roles', methods=['POST'])
@requires_permission([Permissions.USERS_ADMIN])
def add_role():
    """
        Add role.
        ---
        definitions:
          - schema:
              id: Role
              properties:
                name:
                 type: string
                 description: role name
                default:
                 type: boolean
                 description: is default
                permissions:
                 type: array
                 description: List of permissions
                 items:
                    oneOf:
                      - $ref: "#/definitions/Permission"
        parameters:
            - in: body
              name: role
              required: true
              description: role
              schema:
                  $ref: "#/definitions/Role"
        responses:
                200:
                    description: New role.
                    schema:
                        $ref: '#/definitions/Role'
                401:
                    description: Invalid username or password.
    """
    _request = from_json(request.data.decode('utf-8'))
    api_role = api.Role(**_request)
    existing_role = Role.query.filter_by(name=api_role.name).first()
    if existing_role:
        raise ValidationError('Role already exists.')
    permissions = []
    for api_permission in api_role.permissions:
        permission = Permission.query.filter_by(name=api_permission.name).first()
        if not permission:
            raise ValidationError(f'Permission {api_permission.name} not found.')
        permissions.append(permission)
    role = Role(name=api_role.name, default=api_role.default, permissions=permissions)
    db.session.add(role)
    db.session.commit()
    return jsonify(api.Role.from_orm(role).dict()), 200


@token_auth.route('/roles/<name>', methods=['PUT'])
@requires_permission([Permissions.USERS_ADMIN])
def update_role(name):
    """
        Update role permissions.
        ---
        parameters:
            - in: body
              name: role
              required: true
              description: role
              schema:
                  $ref: "#/definitions/Role"
        responses:
                200:
                    description: Updated role.
                    schema:
                        $ref: '#/definitions/Role'
                401:
                    description: Invalid username or password.
    """
    _request = from_json(request.data.decode('utf-8'))
    api_role = api.Role(**_request)
    role = Role.query.filter_by(name=api_role.name).first()
    if not role:
        return jsonify('Role not found.'), 404
    role.reset_permissions()
    if role.name != name:
        return jsonify('Invalid role name.'), 400
    if (not api_role.permissions) or len(api_role.permissions) == 0:
        raise ValidationError('Invalid permissions.')
    for api_permission in api_role.permissions:
        permission = Permission.query.filter_by(name=api_permission.name).first()
        if not permission:
            raise ValidationError(f'Permission {api_permission.name} not found.')
        role.add_permission(permission)
    db.session.commit()
    return jsonify(api.Role.from_orm(role).dict()), 200


@users.route('/', methods=['POST'], strict_slashes=False)
@requires_permission([Permissions.USERS_ADMIN])
def add_user():
    """
        Add user.
        ---
        parameters:
            - in: body
              name: user
              required: true
              description: role
              schema:
                  $ref: "#/definitions/User"
        responses:
                200:
                    description: New user.
                    schema:
                        $ref: '#/definitions/User'
                401:
                    description: Invalid username or password.
    """
    _request = from_json(request.data.decode('utf-8'))
    api_user = api.CreateUser(**_request)
    user = User.query.filter(or_(User.username == api_user.username, User.email == api_user.email)).first()
    if user:
        raise ValidationError('User already registered.')
    role = Role.query.filter_by(name=api_user.role.name).first()
    if not role:
        raise ValidationError('Invalid role.')
    user = User(username=api_user.username, login_type=LoginType.BASIC, email=api_user.email, role=role,
                password=api_user.password)
    db.session.add(user)
    db.session.commit()
    return jsonify(api.User.from_orm(user).dict()), 200


@users.route('/<username>', methods=['PUT'])
@requires_permission([Permissions.USERS_ADMIN])
def update_user(username):
    """
        Update user.
        ---

        parameters:
            - in: body
              name: user
              required: true
              description: user
              schema:
                  $ref: "#/definitions/User"
        responses:
                200:
                    description: Updated user.
                    schema:
                        $ref: '#/definitions/User'
                401:
                    description: Invalid username or password.
    """
    _request = from_json(request.data.decode('utf-8'))
    api_user = api.User(**_request)
    user = User.query.filter_by(username=api_user.username).first()
    if not user:
        return jsonify('User not found.'), 404
    if user.username != username:
        return jsonify('Invalid username.'), 404
    if api_user.email and user.email != api_user.email:
        _user = User.query.filter_by(email=api_user.email).first()
        if _user:
            return jsonify('Email already assigned.'), 404
        user.email = api_user.email

    role = Role.query.filter_by(name=api_user.role.name).first()
    if not role:
        return jsonify('Invalid role.'), 404
    user.role = role
    db.session.commit()
    return jsonify(api.User.from_orm(user).dict()), 200


@token_auth.route('/permissions', methods=['POST'])
@requires_permission([Permissions.USERS_ADMIN])
def add_permission():
    """
        Add permission.
        ---
        definitions:
          - schema:
              id: Permission
              properties:
                id:
                 type: string
                 description: permission id
                name:
                 type: string
                 description: permission name

        parameters:
            - in: body
              name: permission
              required: true
              description: permission
              schema:
                  $ref: "#/definitions/Permission"
        responses:
                200:
                    description: New permission.
                    schema:
                        $ref: '#/definitions/Permission'
                401:
                    description: Authentication error.
                403:
                    description: Forbidden.
    """
    _request = from_json(request.data.decode('utf-8'))
    api_permission = api.Permission(**_request)
    existing_permission = Permission.query.filter_by(name=api_permission.name).first()
    if existing_permission:
        raise ValidationError('Permission already exists.')
    permission = Permission(id=api_permission.name, name=api_permission.name)
    db.session.add(permission)
    db.session.commit()
    return jsonify(api.Permission.from_orm(permission).dict()), 200


@token_auth.after_request
@users.after_request
def apply_cors(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response
