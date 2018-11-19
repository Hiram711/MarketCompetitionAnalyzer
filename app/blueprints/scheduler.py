#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
import time

from flask import Blueprint, jsonify, redirect, url_for, current_app
from flask_login import current_user

from app.crawlers.tasks import task_MU
from app.extensions.flaskapscheduler import scheduler
from app.models.auth import Permission

scheduler_bp = Blueprint('scheduler', __name__)


# for test purpose,set it to post and get,before deployment it should be set to only post
@scheduler_bp.route('/start', methods=['POST', 'GET'])
def start_scheduler():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    if scheduler.state == 0:
        scheduler.start()  # start APscheduler and run jobs
    if scheduler.state == 2:
        scheduler.resume()
    return redirect(url_for('scheduler.get_status'))


# for test purpose,set it to post and get,before deployment it should be set to only post
@scheduler_bp.route('/shutdown', methods=['POST', 'GET'])
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


@scheduler_bp.route('/allJobs')
def get_all_jobs():
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


# a test job
def job1(a, b):
    print(str(a) + ' ' + str(b) + '   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# for test purpose,set it to post and get,before deployment it should be set to only post
@scheduler_bp.route('/add')
def add_job():
    if not (current_user.is_authenticated and current_user.can(Permission.MANAGE_CRAWLER)):
        return jsonify(message='Login or privileges required.'), 403
    scheduler.add_job(id='test', func=job1, args=('hello', 'flask'), trigger='interval', seconds=20,
                      replace_existing=True)
    scheduler.add_job(id='test_selenium', func=task_MU, args=(current_app.config['SQLALCHEMY_DATABASE_URI'], 1),
                      trigger='interval', hours=4, replace_existing=True)
    return redirect(url_for('scheduler.get_all_jobs'))
