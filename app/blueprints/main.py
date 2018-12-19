#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    return render_template('main/analysis.html')


@main_bp.route('/hello')
def hello():
    return 'Hello World!'

