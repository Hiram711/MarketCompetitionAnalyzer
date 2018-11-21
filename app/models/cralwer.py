#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from datetime import datetime

from flask import current_app

from app.extensions.flasksqlalchemy import db


class CrawlerLog(db.Model):
    __tablename__ = 'crawler_logs'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    segment_id = db.Column(db.Integer, db.ForeignKey('segments.id'))
    flight_date = db.Column(db.Date)
    begin_date = db.Column(db.DateTime, default=datetime.now())
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Running')
    rowcnt = db.Column(db.Integer)
    details = db.Column(db.Text)


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(40), index=True, unique=True)
    prefix = db.Column(db.String(10), index=True, unique=True)
    is_avaliable = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    modify_time = db.Column(db.DateTime, default=datetime.now)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    run_logs = db.relationship('CrawlerLog', backref='company', lazy='dynamic')
    prices = db.relationship('Price', backref='company', lazy='dynamic')
    prices_details = db.relationship('PriceDetail', backref='company', lazy='dynamic')

    def to_json(self):
        return {'id': self.id, 'company_name': self.company_name, 'prefix': self.prefix,
                'is_avaliable': self.is_avaliable,
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'modify_time': self.modify_time.strftime('%Y-%m-%d %H:%M:%S'),
                'editor': self.editor.username}

    @property
    def crawler_func(self):
        return current_app.config['CRAWLER_FUNCS'].get(self.prefix)

    @staticmethod
    def insert_companies():
        companies = current_app.config['CRAWLER_COMPANY']
        for r in companies:
            company = Company.query.filter_by(company_name=r).first()
            if company is None:
                company = Company(company_name=r)
            company.prefix = companies[r]
            company.editor_id = 1
            db.session.add(company)
        db.session.commit()


class Segment(db.Model):
    __tablename__ = 'segments'
    id = db.Column(db.Integer, primary_key=True)
    dep_city = db.Column(db.String(40))
    arv_city = db.Column(db.String(40))
    create_time = db.Column(db.DateTime, default=datetime.now)
    modify_time = db.Column(db.DateTime, default=datetime.now)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    run_logs = db.relationship('CrawlerLog', backref='segment', lazy='dynamic')
    prices = db.relationship('Price', backref='segment', lazy='dynamic')
    prices_details = db.relationship('PriceDetail', backref='segment', lazy='dynamic')

    def to_json(self):
        return {'id': self.id, 'dep_city': self.dep_city, 'arv_city': self.arv_city,
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'modify_time': self.modify_time.strftime('%Y-%m-%d %H:%M:%S'),
                'editor': self.editor.username}


# we specify this special model because every company according to the situation will have some special price plans
class PriceDetail(db.Model):
    __tablename__ = 'price_details'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    segment_id = db.Column(db.Integer, db.ForeignKey('segments.id'))
    get_time = db.Column(db.DateTime, nullable=False, index=True)  # when we get this data
    dep_airport = db.Column(db.String(40))
    arv_airport = db.Column(db.String(40))
    flight_no = db.Column(db.String(20))  # like 'MU9825'
    flight_date = db.Column(db.Date)  # like date'2018-10-04'
    airplane_type = db.Column(db.String(40))  # like '330','737',should cut the string '空客','波音','机型' ..etc
    dep_time = db.Column(db.String(20))  # departure time, like '08:00'
    arv_time = db.Column(db.String(20))  # arrive time ,same as dep_time
    flight_time = db.Column(db.String(20))  # means how long the flight takes,like '2小时15分'
    is_direct = db.Column(db.Boolean)  # if false you should fill in the transfer_city
    transfer_city = db.Column(db.String(40))  # like '遵义'
    is_shared = db.Column(
        db.Boolean)  # shared tag, means some flights belonging to other company is on sale in the target company website
    share_company = db.Column(db.String(20))  # like '上海航空', no needs to associate with the Model Company
    share_flight_no = db.Column(db.String(20))
    price_type1 = db.Column(
        db.String(40))  # the base type of pirce.it may contains several sub types which is defined as price_type2
    price_type2 = db.Column(db.String(40))  # can be complex，like '头等舱 (P)','全价经济舱' ..etc
    discount = db.Column(db.Numeric(5, 2))  # like 0.18.means '1.8折'
    price = db.Column(db.Integer)  # like 1700


# use this model to save data after cleaning the table price_details(maybe by a database procedure)
class Price(db.Model):
    __tablename__ = 'prices'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    segment_id = db.Column(db.Integer, db.ForeignKey('segments.id'))
    get_time = db.Column(db.DateTime, nullable=False, index=True)
    flight_no = db.Column(db.String(20))
    flight_date = db.Column(db.Date)
    airplane_type = db.Column(db.String(40))
    dep_time = db.Column(db.DateTime)
    arv_time = db.Column(db.DateTime)
    flight_time = db.Column(db.Numeric(5, 2))  # by hour
    is_direct = db.Column(db.Boolean)
    transfer_city = db.Column(db.String(40))
    is_shared = db.Column(db.Boolean)
    share_company = db.Column(db.String(20))
    share_flight_no = db.Column(db.String(20))
    price1 = db.Column(db.Integer)
    price2 = db.Column(db.Integer)
    price3 = db.Column(db.Integer)


# use this model to save the user config about crawler running interval
class Interval(db.Model):
    __tablename__ = 'intervals'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, default=2)

    @staticmethod
    def insert_interval():
        i = Interval()
        db.session.add(i)
        db.session.commit()
