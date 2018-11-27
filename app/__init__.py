#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

import os

import click
from flask import Flask

from .blueprints.auth import auth_bp
from .blueprints.main import main_bp
from .blueprints.sysmanage import sysmanage_bp
from .config import config
from .extensions.csrf_protect import csrf
from .extensions.flaskapscheduler import scheduler
from .extensions.flaskmail import mail
from .extensions.flaskmigrate import migrate
from .extensions.flasksqlalchemy import db
from .extensions.loginmanager import login_manager
from .models.auth import Permission, User, Role
from .models.cralwer import CrawlerLog, Company, Segment, Price, PriceDetail, Interval


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask('app')

    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_template_context(app)
    register_commands(app)
    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(sysmanage_bp, url_prefix='/config')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Role=Role, Permission=Permission, Company=Company, CrawlerLog=CrawlerLog,
                    Segment=Segment, Price=Price, PriceDetail=PriceDetail, scheduler=scheduler, Interval=Interval)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        return dict(Permission=Permission)


def register_commands(app):
    @app.cli.command()
    def init():
        """Initialize app."""
        click.echo('Initializing the database...')
        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.insert_roles()

        click.echo('Creating User admin...\naccount:admin@admin.com\npassword:admin')
        admin = User(username='admin', email='admin@admin.com', password='admin')
        admin.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(admin)
        db.session.commit()

        click.echo('Initializing the target Companies...')
        Company.insert_companies()

        click.echo('Initializing the default Interval...')
        Interval.insert_interval()

        click.echo('Done.')
