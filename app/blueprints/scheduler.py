#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from datetime import datetime

from flask import Blueprint, jsonify, redirect, url_for, current_app, request
from flask_login import current_user

from app.extensions.flaskapscheduler import scheduler
from app.extensions.flasksqlalchemy import db
from app.models.auth import Permission
from app.models.cralwer import Company, Interval

scheduler_bp = Blueprint('scheduler', __name__)


@scheduler_bp.route('/start', methods=['POST'])
def start_scheduler():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    if scheduler.state == 0:
        scheduler.start()  # start APscheduler and run jobs
    if scheduler.state == 2:
        scheduler.resume()
    return redirect(url_for('scheduler.get_status'))


@scheduler_bp.route('/shutdown', methods=['POST'])
def shutdown_scheduler():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    if scheduler.state in (1, 2):
        scheduler.shutdown()
    return redirect(url_for('scheduler.get_status'))


@scheduler_bp.route('/status')
def get_status():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    return jsonify(dict(status=scheduler.state)), 200


@scheduler_bp.route('/list')
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


@scheduler_bp.route('/interval/list')
def list_interval():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 401
    config_interval = Interval.query.first().value
    return jsonify(config_interval), 200


# use this view to change the interval
@scheduler_bp.route('/interval/reload', methods=['POST'])
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


@scheduler_bp.route('/company/list')
def list_company():
    if not (current_user.is_authenticated and current_user.can(Permission.VIEW_DATA)):
        return jsonify(message='Login or privileges required.'), 403
    companies = Company.query.all()
    company_list = [company.to_json() for company in companies]
    return jsonify(company_list), 200


@scheduler_bp.route('/company/edit', methods=['POST'])
def edit_company():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    id = request.values.get('id')
    is_avaliable = request.values.get('is_avaliable', default=False, type=bool)
    config_interval = Interval.query.first().value
    company = Company.query.get(id)
    if company:
        company.is_avaliable = is_avaliable
        company.modify_time = datetime.now()
        company.editor = current_user._get_current_object()
        db.session.add(edit_company)
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
