#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

from app.apis.v1 import resources
