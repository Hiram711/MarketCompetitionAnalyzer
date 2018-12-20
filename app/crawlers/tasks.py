#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

import re
from datetime import datetime, timedelta

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from app.crawlers.data_grabber_8L import data_grabber_8l
from app.crawlers.data_grabber_MU import data_grabber_mu
from app.utils import get_rnd_proxy


# make data cleaned and recorded
def task_MU(db_url, add_days=7, use_proxy=False):
    try:
        # create a new data connection using reflection,
        # in this way we can avoid using app context and the fun can run independently
        engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(engine, only=['crawler_logs', 'companies', 'segments', 'price_details', 'prices'])
        Base = automap_base(metadata=metadata)
        Base.prepare()
        CrawlerLog, Company, Segment, PriceDetail, Price = Base.classes.crawler_logs, Base.classes.companies, \
                                                           Base.classes.segments, Base.classes.price_details, \
                                                           Base.classes.prices

        session = Session(engine)
        company = session.query(Company).filter_by(prefix='MU').first()
        segments = session.query(Segment).all()
        begin_date = datetime.now()
        re_time = re.compile(r'\d{2}:\d{2}')
        re_discount = re.compile(r'.*折')
        re_price = re.compile('[0-9.,]+')
        for segment in segments:
            for i in range(add_days):
                query_date = (begin_date + timedelta(days=i)).strftime('%Y-%m-%d')
                proxy = None
                if use_proxy:
                    proxy = get_rnd_proxy()
                log = CrawlerLog()
                log.status = 'Running'
                log.company_id = company.id
                log.segment_id = segment.id
                get_time = datetime.now()
                log.begin_date = get_time
                log.flight_date = (begin_date + timedelta(days=i)).date()
                session.add(log)
                session.commit()
                log = session.query(CrawlerLog).get(log.id)
                try:
                    # result= data_grabber_mu(segment.dep_city,segment.arv_city,flight_date=query_date,proxy=proxy)
                    result = data_grabber_mu(segment.dep_city, segment.arv_city, flight_date=query_date, proxy=proxy)
                    for row in result:
                        for subrow in row['price_list']:
                            dt = PriceDetail()
                            dt.get_time = get_time
                            dt.company_id = company.id
                            dt.segment_id = segment.id
                            dt.dep_time = re_time.findall(row['dpt'])[0].strip()
                            dt.dep_airport = re_time.split(row['dpt'])[1].strip()
                            dt.arv_time = re_time.findall(row['arrv'])[0].strip()
                            dt.arv_airport = re_time.split(row['arrv'])[-1].strip()
                            dt.flight_no = row['fltno'].strip()
                            dt.flight_date = (begin_date + timedelta(days=i)).date()
                            dt.airplane_type = row['airplane_type'].strip()
                            dt.flight_time = row['flt_tm'].strip()
                            if row['is_direct'] == '经停':
                                dt.is_direct = False
                            elif row['is_direct'] == '直达':
                                dt.is_direct = True
                            dt.transfer_city = row['mid'].strip()
                            if row['company'] != '东方航空':
                                dt.is_shared = True
                                dt.share_company = row['company'].strip()
                                dt.share_flight_no = row['fltno'].strip()
                            dt.price_type1 = subrow[0]
                            dt.price_type2 = subrow[1]
                            if re_discount.match(subrow[2]):
                                dt.discount = float(re_price.findall(re_discount.findall(subrow[2])[0].strip())[
                                                        0]) / 10
                                dt.price = int(re.sub(r',{1}', '', re_price.findall(subrow[2])[1].strip()))
                            else:
                                dt.discount = 1
                                dt.price = int(re.sub(r',{1}', '', re_price.findall(subrow[2])[0].strip()))
                            session.add(dt)
                            session.commit()
                    log.status = 'Success'
                    log.rowcnt = len(result)
                except Exception as e:
                    log.details = str(e)
                    log.status = 'Failed'
                finally:
                    log.end_date = datetime.now()
                session.add(log)
                session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def task_8L(db_url, add_days=7, use_proxy=False):
    try:
        # create a new data connection using reflection,
        # in this way we can avoid using app context and the fun can run independently
        engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(engine, only=['crawler_logs', 'companies', 'segments', 'price_details', 'prices'])
        Base = automap_base(metadata=metadata)
        Base.prepare()
        CrawlerLog, Company, Segment, PriceDetail, Price = Base.classes.crawler_logs, Base.classes.companies, \
                                                           Base.classes.segments, Base.classes.price_details, \
                                                           Base.classes.prices

        session = Session(engine)
        company = session.query(Company).filter_by(prefix='8L').first()
        segments = session.query(Segment).all()
        begin_date = datetime.now()
        for segment in segments:
            for i in range(add_days):
                query_date = (begin_date + timedelta(days=i)).strftime('%Y-%m-%d')
                proxy = None
                if use_proxy:
                    proxy = get_rnd_proxy()
                log = CrawlerLog()
                log.status = 'Running'
                log.company_id = company.id
                log.segment_id = segment.id
                get_time = datetime.now()
                log.begin_date = get_time
                log.flight_date = (begin_date + timedelta(days=i)).date()
                session.add(log)
                session.commit()
                log = session.query(CrawlerLog).get(log.id)
                try:
                    # result= data_grabber_mu(segment.dep_city,segment.arv_city,flight_date=query_date,proxy=proxy)
                    result = data_grabber_8l(segment.dep_city, segment.arv_city, flight_date=query_date, proxy=proxy)

                    # solve the situation that one city has more than one airports
                    if segment.dep_city == '上海':
                        result_more = data_grabber_8l('上海浦东', segment.arv_city, flight_date=query_date)
                        result.extend(result_more)
                    if segment.arv_city == '上海':
                        result_more = data_grabber_8l(segment.dep_city, '上海浦东', flight_date=query_date)
                        result.extend(result_more)

                    for row in result:
                        dt = PriceDetail()
                        dt.get_time = get_time
                        dt.company_id = company.id
                        dt.segment_id = segment.id
                        dt.get_time = get_time
                        dt.company_id = company.id
                        dt.segment_id = segment.id
                        dt.dep_time = datetime.strptime(row['dep_date'].strip(), '%Y-%m-%d %H:%M').strftime('%H:%M')
                        dt.dep_airport = row['dep_airport'].strip()
                        dt.arv_time = datetime.strptime(row['arv_date'].strip(), '%Y-%m-%d %H:%M').strftime('%H:%M')
                        dt.arv_airport = row['arv_airport'].strip()
                        dt.flight_no = row['flt_no'].strip()
                        dt.flight_date = (begin_date + timedelta(days=i)).date()
                        dt.airplane_type = row['airplane_type'].strip()
                        dt.flight_time = row['flt_time'].strip()
                        dt.is_direct = row['is_direct']
                        dt.transfer_city = row['transfer_city'].strip()
                        dt.price_type1 = row['price_class1']
                        dt.price_type2 = row['price_class2']
                        dt.price = float(row['price_value'].strip())
                        session.add(dt)
                        session.commit()
                    log.status = 'Success'
                    log.rowcnt = len(result)
                except Exception as e:
                    log.details = str(e)
                    log.status = 'Failed'
                finally:
                    log.end_date = datetime.now()
                session.add(log)
                session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


if __name__ == '__main__':
    # task_MU(db_url='sqlite:///C:\\Users\\jie.zhang8\\Desktop\\MarketCompetitionAnalyzer\\data-dev.db', add_days=1)
    task_8L(db_url='sqlite:///C:\\Users\\jie.zhang8\\Desktop\\MarketCompetitionAnalyzer\\data-dev.db', add_days=1)
