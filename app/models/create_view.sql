create or replace view v_price_details as
SELECT b.dep_city,b.arv_city,c.company_name,a.*
FROM price_details a
LEFT JOIN segments b on a.segment_id=b.id
LEFT JOIN companies c on a.company_id=c.id
where a.id in
(SELECT  max(id)
FROM price_details
GROUP BY company_id,segment_id,flight_no,flight_date,price_type1,price_type2);

create or replace view v_price_overview as
SELECT company_id,company_name,segment_id,dep_city,arv_city,flight_no,flight_date,dep_time,arv_time
,case
when price_type1='标准经济舱' and company_name='祥鹏航空' then 'economy'
when price_type1='优惠经济舱' and company_name='祥鹏航空' then 'member'
when price_type1='公务舱' and company_name='祥鹏航空' then 'luxury'
else price_type1
end as price_type1
,min(price) as price
FROM
v_price_details
group by company_id,company_name,segment_id,dep_city,arv_city,flight_no,flight_date,dep_time,arv_time
,case
when price_type1='标准经济舱' and company_name='祥鹏航空' then 'economy'
when price_type1='优惠经济舱' and company_name='祥鹏航空' then 'member'
when price_type1='公务舱' and company_name='祥鹏航空' then 'luxury'
else price_type1
end;