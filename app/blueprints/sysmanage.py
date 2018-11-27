#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

import json
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, Markup
from flask import redirect, url_for, current_app
from flask_login import current_user, login_required
from sqlalchemy import text

from app.extensions.flaskapscheduler import scheduler
from app.extensions.flasksqlalchemy import db
from app.models.auth import User, Permission, Role
from app.models.cralwer import Company, Interval
from app.models.cralwer import Segment

sysmanage_bp = Blueprint('sysmanage', __name__)


@sysmanage_bp.route('/')
@login_required
def index():
    return render_template('sysmanage/config.html')


@sysmanage_bp.route('/user')
@login_required
def user_index():
    return render_template('sysmanage/user.html')


# ajax
@sysmanage_bp.route('/user/list')
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
        pagination = User.query.filter_by(**filters).order_by(text(sidx + ' ' + sord)).paginate(page, per_page)
    else:
        pagination = User.query.order_by(text(sidx + ' ' + sord)).paginate(page, per_page)
    users = pagination.items
    users_list = [user.to_json() for user in users]
    result = {'total': pagination.total, 'pages': pagination.pages, 'page': pagination.page,
              'per_page': pagination.per_page, 'users': users_list}
    return jsonify(result), 200


# ajax
@sysmanage_bp.route('/user/edit', methods=['POST'])
def edit_user():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 401
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
        return jsonify(message='Invalid parameters..'), 400


# ajax
@sysmanage_bp.route('/role/list')
def list_role():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 401
    roles = Role.query.all()
    roles_select = '<select>'
    for i in roles:
        roles_select += "<option value='%s'>%s</option>" % (i.id, i.name)
    roles_select += '</select>'
    return Markup(roles_select)


# ajax
@sysmanage_bp.route('/segment/list')
def list_segment():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 403
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('rows', 10, type=int)
    sidx = request.args.get('sidx', 'id', type=str)
    sord = request.args.get('sord', 'asc', type=str)
    _search = request.args.get('_search', 'false', type=str)
    if _search == 'true':
        filters = request.args.get('filters', '', type=str)
        filters = json.loads(filters)
        group_op = filters.get('groupOp', 'AND')
        rules = filters.get('rules', [])
        filters = {}
        for i in rules:
            if i.get('op') == 'eq':
                filters[i.get('field')] = i.get('data')
        if group_op == 'AND':
            pagination = Segment.query.filter_by(**filters).order_by(text(sidx + ' ' + sord)).paginate(page, per_page)
        elif group_op == 'OR':
            filter_str = "1=2"
            for k, v in filters.items():
                filter_str = filter_str + ' or ' + "%s='%s'" % (k, v)
            pagination = Segment.query.filter(text(filter_str)).order_by(text(sidx + ' ' + sord)).paginate(page,
                                                                                                           per_page)
    else:
        pagination = Segment.query.order_by(text(sidx + ' ' + sord)).paginate(page, per_page)
    segments = pagination.items
    segment_list = [segment.to_json() for segment in segments]
    result = {'total': pagination.total, 'pages': pagination.pages, 'page': pagination.page,
              'per_page': pagination.per_page, 'segments': segment_list}
    return jsonify(result), 200


# ajax
@sysmanage_bp.route('/segment/edit', methods=['POST'])
def edit_segment():
    if not (current_user.is_authenticated and current_user.can(Permission.MAGAGE_USER)):
        return jsonify(message='Login or privileges required.'), 401
    id = request.form.get('id')
    oper = request.form.get('oper')
    if id is not None and oper == 'del':
        segment = Segment.query.get(id)
        if segment is None:
            return jsonify(message='Segment delete failed.'), 400
        db.session.delete(segment)
        return jsonify(message='Segment deleted.'), 200
    elif oper == 'add':
        segment = Segment()
        segment.dep_city = request.form.get('dep_city')
        segment.arv_city = request.form.get('arv_city')
        segment.editor = current_user._get_current_object()
        db.session.add(segment)
        return jsonify(message='Segment created.'), 200
    elif id is not None and oper == 'edit':
        segment = Segment.query.get(int(id))
        segment.dep_city = request.form.get('dep_city')
        segment.arv_city = request.form.get('arv_city')
        segment.editor = current_user._get_current_object()
        segment.modify_time = datetime.now()
        db.session.add(segment)
        return jsonify(message='Segment changed.'), 200
    else:
        return jsonify(message='Invalid parameters..'), 400


@sysmanage_bp.route('/company/list')
def list_company():
    if not (current_user.is_authenticated and current_user.can(Permission.VIEW_DATA)):
        return jsonify(message='Login or privileges required.'), 403
    companies = Company.query.all()
    company_list = [company.to_json() for company in companies]
    return jsonify(company_list), 200


@sysmanage_bp.route('/company/edit', methods=['POST'])
def edit_company():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    id = request.values.get('id')
    is_avaliable = True if request.values.get('is_avaliable') == 'true' else False
    config_interval = Interval.query.first().value
    company = Company.query.get(id)
    if company:
        company.is_avaliable = is_avaliable
        company.modify_time = datetime.now()
        company.editor = current_user._get_current_object()
        db.session.add(company)
        if is_avaliable:
            scheduler.add_job(id=str(company.id), func=company.crawler_func,
                              args=(current_app.config['SQLALCHEMY_DATABASE_URI'], current_app.config['CRAWLER_DAYS']),
                              trigger='interval', hours=config_interval, replace_existing=True)
            return jsonify(message='Job added'), 200
        else:
            if scheduler.get_job(str(company.id)):
                scheduler.remove_job(str(company.id))
            return jsonify(message='Job deleted'), 200
    else:
        return jsonify(message='Invalid parameters.'), 400


@sysmanage_bp.route('/interval/list')
def list_interval():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 401
    config_interval = Interval.query.first().value
    return jsonify(config_interval), 200


# use this view to change the interval
@sysmanage_bp.route('/interval/reload', methods=['POST'])
def reload_interval():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 401
    new_interval = request.values.get('interval')
    config_interval = Interval.query.first()
    config_interval.value = new_interval
    db.session.add(config_interval)
    companies = Company.query.filter_by(is_avaliable=True).all()
    for company in companies:
        scheduler.add_job(id=str(company.id), func=company.crawler_func,
                          args=(current_app.config['SQLALCHEMY_DATABASE_URI'], current_app.config['CRAWLER_DAYS']),
                          trigger='interval', hours=new_interval, replace_existing=True)
    return jsonify(message='Interval changed.'), 200


@sysmanage_bp.route('/scheduler/start', methods=['POST'])
def start_scheduler():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    if scheduler.state == 0:
        scheduler.start()  # start APscheduler and run jobs
    if scheduler.state == 2:
        scheduler.resume()
    return redirect(url_for('sysmanage.get_scheduler_status'))


@sysmanage_bp.route('/scheduler/shutdown', methods=['POST'])
def shutdown_scheduler():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    if scheduler.state in (1, 2):
        scheduler.shutdown()
    return redirect(url_for('sysmanage.get_scheduler_status'))


@sysmanage_bp.route('/scheduler/status')
def get_scheduler_status():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    return jsonify(dict(status=scheduler.state)), 200


@sysmanage_bp.route('/scheduler/list')
def list_job():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    result = []
    if scheduler.state == 0:
        scheduler.start()
        scheduler.pause()
    for i in scheduler.get_jobs():
        item = dict(id=i.id, name=i.name, args=i.args, kwargs=i.kwargs, next_run_time=i.next_run_time,
                    func=i.func.__name__)
        result.append(item)
    return jsonify(result), 200
