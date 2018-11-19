#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, Markup
from flask_login import current_user, login_user, login_required, logout_user

from app.extensions.flasksqlalchemy import db
from app.forms.auth import LoginForm
from app.models.auth import User, Permission, Role
from app.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_back()

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('Login success.', 'info')
                return redirect_back()
        flash('Invalid email or password.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/user')
@login_required
def user_index():
    return render_template('auth/users.html')


# ajax
@auth_bp.route('/user/list')
def list_user():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 403
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('rows', 10, type=int)
    sidx = request.args.get('sidx', 'id', type=str)
    sord = request.args.get('sord', 'asc', type=str)
    _search = request.args.get('_search', 'false', type=str)
    search_field = request.args.get('searchField', '', type=str)
    search_oper = request.args.get('searchOper', '', type=str)
    search_string = request.args.get('searchString', '', type=str)
    if _search == 'true':
        filters = {search_field: search_string}
        pagination = User.query.filter_by(**filters).order_by(sidx + ' ' + sord).paginate(page, per_page)
    else:
        pagination = User.query.order_by(sidx + ' ' + sord).paginate(page, per_page)
    users = pagination.items
    users_list = [user.to_json() for user in users]
    result = {'total': pagination.total, 'pages': pagination.pages, 'page': pagination.page,
              'per_page': pagination.per_page, 'users': users_list}
    return jsonify(result), 200


# ajax
@auth_bp.route('/user/edit', methods=['POST'])
def edit_user():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 403
    id = request.form.get('id')
    oper = request.form.get('oper')
    if id is not None and oper == 'del':
        user = User.query.get(id)
        if user is None or user == current_user:
            return jsonify(message='User delete failed.'), 400
        db.session.delete(user)
        return jsonify(message='User deleted.'), 200
    elif oper == 'add':
        user = User()
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role_id = request.form.get('role')
        db.session.add(user)
        return jsonify(message='User created.'), 200
    elif id is not None and oper == 'edit':
        user = User.query.get(int(id))
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role_id = request.form.get('role')
        user.modify_time = datetime.now()
        db.session.add(user)
        return jsonify(message='User changed.'), 200
    else:
        return jsonify(message='Invalid parameters..'), 401


# ajax
@auth_bp.route('/role/list')
def list_role():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 403
    roles = Role.query.all()
    roles_select = '<select>'
    for i in roles:
        roles_select += "<option value='%s'>%s</option>" % (i.id, i.name)
    roles_select += '</select>'
    return Markup(roles_select)
