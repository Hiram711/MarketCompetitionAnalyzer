#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions.flasksqlalchemy import db
from app.extensions.loginmanager import login_manager


class Permission:
    VIEW_DATA = 0x01
    MAGAGE_USER = 0x02
    MANAGE_CRAWLER = 0x04
    ADMINISTER = 0x80


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, index=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime, default=datetime.now)
    modify_time = db.Column(db.DateTime, default=datetime.now)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=1)
    edit_company = db.relationship('Company', backref='editor', lazy='dynamic')
    edit_segment = db.relationship('Segment', backref='editor', lazy='dynamic')

    def to_json(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'role': self.role.name,
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'modify_time': self.modify_time.strftime('%Y-%m-%d %H:%M:%S')}

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {'User': (Permission.VIEW_DATA, True),
                 'Manager': (Permission.VIEW_DATA | Permission.MAGAGE_USER, False),
                 'Administrator': (0xff, False)}
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name
