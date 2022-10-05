from __future__ import annotations
import datetime
from enum import Enum
from typing import List

from flask import current_app
from itsdangerous import Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from hodor import db


class ValidationError(ValueError):
    pass


class Permissions(Enum):
    BOOKS_ADD = 'books:add'
    BOOKS_READ = 'books:read'
    BOOKS_WRITE = 'books:write'
    USERS_ADMIN = 'users:admin'
    USERS_PROFILE = 'users:profile'


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(2000), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    login_type = db.Column(db.String(64), default='basic')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship("Role", back_populates="users")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def get_basic_user(email: str):
        return User.query.filter_by(email=email).filter_by(login_type=LoginType.BASIC).first()

    def to_json(self):
        return {'id': self.id,
                'username': self.username,
                'email': self.email,
                'login_type': self.login_type,
                'roles': [self.role.name],
                'permissions': [p.id for p in self.role.permissions]}

    @staticmethod
    def from_dict(data: dict):
        return User(**data)

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    @staticmethod
    def insert_users(config):
        users = [{'username': config['admin_user'], 'email': 'admin@gmail.com',
                  'password': config["admin_password"], 'role': 'ROLE_ADMIN'},
                 {'username': config['guest_user'], 'email': 'guest@gmail.com',
                  'password': config["guest_password"], 'role': 'ROLE_USER'},
                 {'username': 'moderator', 'email': 'moderator@gmail.com',
                  'password': config["guest_password"], 'role': 'ROLE_MODERATOR'}
                 ]

        for user in users:
            existing_user = User.query.filter_by(username=user['username']).first()
            if existing_user is None:
                role = Role.query.filter_by(name=user['role']).first()
                user_entity = User(username=user['username'], email=user['email'],
                                   password=user['password'],
                                   role=role)
                db.session.add(user_entity)
        db.session.commit()

    @staticmethod
    def get_all() -> List[User]:
        default_role = Role.query.filter_by(default=True).first()
        _users = User.query.all()
        for _user in _users:
            if _user.role is None:
                _user.role = default_role
        return _users


role_permissions = db.Table(
    'roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.String(64), db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.relationship('Permission', secondary=role_permissions, back_populates="roles")
    users = db.relationship('User', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = []

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions.append(perm)

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions.remove(perm)

    def reset_permissions(self):
        self.permissions = []

    def has_permission(self, perm):
        return perm in self.permissions

    @staticmethod
    def insert_roles():
        roles = {
            'ROLE_USER': [Permissions.BOOKS_ADD, Permissions.BOOKS_READ, Permissions.BOOKS_WRITE,
                          Permissions.USERS_PROFILE],
            'ROLE_MODERATOR': [Permissions.USERS_PROFILE],
            'ROLE_ADMIN': [Permissions.BOOKS_ADD, Permissions.BOOKS_READ, Permissions.BOOKS_WRITE,
                           Permissions.USERS_PROFILE, Permissions.USERS_ADMIN],
        }
        default_role = 'ROLE_USER'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                _permission = Permission.query.filter_by(name=perm.value).first()
                role.add_permission(_permission)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    roles = db.relationship('Role', secondary=role_permissions, back_populates="permissions")

    def __init__(self, **kwargs):
        super(Permission, self).__init__(**kwargs)

    def __eq__(self, other):
        return other and other.id == self.id

    def to_enum(self) -> Permissions:
        return Permissions(self.name)

    def as_dict(self):
        return {'id': self.id, 'name': self.name}

    @staticmethod
    def from_enum(perm: Permissions):
        return Permission(id=perm.value, name=perm.value)

    @staticmethod
    def from_str(perm: str):
        return Permission(id=perm, name=perm)

    @staticmethod
    def insert_permissions():
        for permission in Permissions:
            _permission = Permission.query.filter_by(name=permission.value).first()
            if _permission is None:
                _permission = Permission(id=permission.value, name=permission.value)
                db.session.add(_permission)
        db.session.commit()


class LoginType:
    BASIC = 'basic'
    GOOGLE = 'google'
