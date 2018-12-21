#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
import re

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required

from app.extensions.flasksqlalchemy import db
from app.models.cralwer import Segment

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    return render_template('main/index.html')


@main_bp.route('/analysis/overview')
@login_required
def analysis_overview_index():
    return render_template('main/analysis.html')


@main_bp.route('/select/segments')
@login_required
def analysis_segments():
    segments = Segment.query.all()
    segment_list = [segment.to_json() for segment in segments]
    return jsonify(segment_list), 200


@main_bp.route('/analysis/overview/query')
def analysis_overview_query():
    segment_id = request.args.get('segment_id', None, type=int)
    flight_date = request.args.get('flight_date', None, type=str)
    price_type = request.args.get('price_type', None, type=str)

    if not (segment_id and flight_date and price_type):
        return jsonify(message='Invalid parameters..'), 400
    if not (re.match(r'\d{4}-\d{2}-\d{2}', flight_date)):
        return jsonify(message='Invalid parameters..'), 400
    if not (isinstance(segment_id, int)):
        return jsonify(message='Invalid parameters..'), 400
    if not (price_type in ('economy', 'member', 'luxury')):
        return jsonify(message='Invalid parameters..'), 400

    analysis_sql = '''
     SELECT segment_id,CONCAT(dep_city,'-',arv_city) seg,SUBSTRING(dep_time,1,2) as time_value,count(distinct flight_no)flts_cnt,count(distinct company_id) company_cnt,
    (SELECT concat(company_name,':',price) FROM v_price_overview where segment_id=t.segment_id and flight_date=t.flight_date and price_type1_alias=t.price_type1_alias and SUBSTRING(dep_time,1,2)=SUBSTRING(t.dep_time,1,2) order by price limit 1) as mkt_min,
    (SELECT concat(company_name,':',price) FROM v_price_overview where segment_id=t.segment_id and flight_date=t.flight_date and price_type1_alias=t.price_type1_alias and SUBSTRING(dep_time,1,2)=SUBSTRING(t.dep_time,1,2) order by price desc limit 1) as mkt_max,
    (SELECT flight_no FROM v_price_overview where segment_id=t.segment_id and flight_date=t.flight_date and price_type1_alias=t.price_type1_alias and SUBSTRING(dep_time,1,2)=SUBSTRING(t.dep_time,1,2) and company_name='祥鹏航空' order by price limit 1) as 8l_flt,
    (SELECT concat(dep_time,'-',arv_time) FROM v_price_overview where segment_id=t.segment_id and flight_date=t.flight_date and price_type1_alias=t.price_type1_alias and SUBSTRING(dep_time,1,2)=SUBSTRING(t.dep_time,1,2) and company_name='祥鹏航空' order by price limit 1) as 8l_time,
    (SELECT price FROM v_price_overview where segment_id=t.segment_id and flight_date=t.flight_date and price_type1_alias=t.price_type1_alias and SUBSTRING(dep_time,1,2)=SUBSTRING(t.dep_time,1,2) and company_name='祥鹏航空' order by price limit 1) as 8l_price
    FROM
    v_price_overview t
    where segment_id=%s
    and flight_date='%s' 
    and price_type1_alias='%s'
    group by segment_id,CONCAT(dep_city,'-',arv_city),SUBSTRING(dep_time,1,2)
    order by SUBSTRING(dep_time,1,2)
    ''' % (segment_id, flight_date, price_type)

    time_sql = '''
    SELECT company_name,max(get_time) get_time 
    FROM v_price_details
    where segment_id=%s
    and flight_date='%s'
    group by company_name;
    ''' % (segment_id, flight_date)

    rs_data = db.session.execute(analysis_sql).fetchall()
    rs_timeinfo = db.session.execute(time_sql).fetchall()

    rs_data_list = []
    col_list = ['segment_id', 'segment', 'time_range', 'flt_cnt', 'company_cnt', 'mkt_min', 'mkt_max', '8L_flt',
                '8L_time', '8L_price']
    for row in rs_data:
        rs_data_list.append(dict(zip(col_list, row)))

    rs_timeinfo_list = []
    for row in rs_timeinfo:
        rs_timeinfo_list.append({'company': row[0], 'get_time': row[1]})
    result = {'data': rs_data_list, 'time_info': rs_timeinfo_list, 'total': len(rs_data_list)}
    return jsonify(result), 200


@main_bp.route('/analysis/detail/query')
@login_required
def analysis_detail_query():
    segment_id = request.args.get('segment_id', None, type=int)
    flight_date = request.args.get('flight_date', None, type=str)
    time_range = request.args.get('time_range', None, type=str)
    price_type1 = request.args.get('price_type1', None, type=str)
    # to do:complete thie view
    return 'To be developed'


@main_bp.route('/analysis/custom')
@login_required
def analysis_custom_index():
    return 'To be developed'
