#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

import os
import sys

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.crawlers.tasks import task_MU, task_8L, task_KY

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:
    MAIL_SUBJECT_PREFIX = '[IT-MCA]'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'abc8@163.com'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or '192.168.0.0.1'
    MAIL_PORT = '25'
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or r'san.zhang'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '123456'

    SECRET_KEY = os.getenv('SECRET_KEY', 'a default secret string')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    CRAWLER_COMPANY = {'东方航空': 'MU',  # set companies
                       '祥鹏航空': '8L',
                       '昆明航空': 'KY'}
    CRAWLER_FUNCS = {'MU': task_MU,
                     '8L': task_8L,
                     'KY': task_KY
                     }  # set different func for different company

    JOBS = []
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'processpool', 'max_workers': 40}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': True,
        'max_instances': 1
    }


class DevelopmentConfig(BaseConfig):
    # SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or prefix + os.path.join(basedir, 'data-dev.db')
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # in-memory database
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
