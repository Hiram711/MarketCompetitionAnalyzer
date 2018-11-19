#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录.'
login_manager.session_protection = 'strong'


@login_manager.user_loader
def load_user(user_id):
    from app.models.auth import User
    return User.query.get(int(user_id))
