create or replace VIEW `v_price_details` AS SELECT
	`b`.`dep_city` AS `dep_city`,
	`b`.`arv_city` AS `arv_city`,
	`c`.`company_name` AS `company_name`,
	`a`.`id` AS `id`,
	`a`.`company_id` AS `company_id`,
	`a`.`segment_id` AS `segment_id`,
	`a`.`get_time` AS `get_time`,
	`a`.`dep_airport` AS `dep_airport`,
	`a`.`arv_airport` AS `arv_airport`,
	`a`.`flight_no` AS `flight_no`,
	`a`.`flight_date` AS `flight_date`,
	`a`.`airplane_type` AS `airplane_type`,
	`a`.`dep_time` AS `dep_time`,
	`a`.`arv_time` AS `arv_time`,
	`a`.`flight_time` AS `flight_time`,
	`a`.`is_direct` AS `is_direct`,
	`a`.`transfer_city` AS `transfer_city`,
	`a`.`is_shared` AS `is_shared`,
	`a`.`share_company` AS `share_company`,
	`a`.`share_flight_no` AS `share_flight_no`,
	`a`.`price_type1` AS `price_type1`,
	`a`.`price_type2` AS `price_type2`,
	`a`.`discount` AS `discount`,
	`a`.`price` AS `price`,
	(
		CASE
		WHEN (
			(
				`a`.`price_type1` = '标准经济舱'
			)
			AND (
				`c`.`company_name` = '祥鹏航空'
			)
		) THEN
			'economy'
		WHEN (
			(
				`a`.`price_type1` = '优惠经济舱'
			)
			AND (
				`c`.`company_name` = '祥鹏航空'
			)
		) THEN
			'member'
		WHEN (
			(
				`a`.`price_type1` = '公务舱'
			)
			AND (
				`c`.`company_name` = '祥鹏航空'
			)
		) THEN
			'luxury'
		WHEN (
			(
				substr(`a`.`price_type1`, 1, 1) = '3'
			)
			AND (
				`c`.`company_name` = '南方航空'
			)
		) THEN
			'economy'
		WHEN (
			(
				substr(`a`.`price_type1`, 1, 1) = '2'
			)
			AND (
				`c`.`company_name` = '南方航空'
			)
		) THEN
			'member'
		WHEN (
			(
				substr(`a`.`price_type1`, 1, 1) IN ('0', '1')
			)
			AND (
				`c`.`company_name` = '南方航空'
			)
		) THEN
			'luxury'
		WHEN (
			(
				`a`.`price_type1` = '经济舱'
			)
			AND (
				`c`.`company_name` = '昆明航空'
			)
		) THEN
			'economy'
		WHEN (
			(
				`a`.`price_type1` IN (
					'优选经济舱',
					'商旅优选',
					'保旅畅游'
				)
			)
			AND (
				`c`.`company_name` = '昆明航空'
			)
		) THEN
			'member'
		WHEN (
			(
				`a`.`price_type1` = '头等舱'
			)
			AND (
				`c`.`company_name` = '昆明航空'
			)
		) THEN
			'luxury'
		WHEN (
			(
				`a`.`price_type1` = '公务舱'
			)
			AND (
				`c`.`company_name` = '四川航空'
			)
		) THEN
			'luxury'
		WHEN (
			(
				`a`.`price_type1` IN (
					'标准经济舱',
					'优选经济舱'
				)
			)
			AND (
				`c`.`company_name` = '四川航空'
			)
		) THEN
			'economy'
		WHEN (
			(
				`a`.`price_type1` IN (
					'优惠经济舱',
					'超值经济舱'
				)
			)
			AND (
				`c`.`company_name` = '四川航空'
			)
		) THEN
			'member'
		ELSE
			`a`.`price_type1`
		END
	) AS `price_type1_alias`
FROM
	(
		(
			`price_details` `a`
			LEFT JOIN `segments` `b` ON (
				(`a`.`segment_id` = `b`.`id`)
			)
		)
		LEFT JOIN `companies` `c` ON (
			(`a`.`company_id` = `c`.`id`)
		)
	)
WHERE
	`a`.`id` IN (
		SELECT
			max(`price_details`.`id`)
		FROM
			`price_details`
		GROUP BY
			`price_details`.`company_id`,
			`price_details`.`segment_id`,
			`price_details`.`flight_no`,
			`price_details`.`flight_date`,
			`price_details`.`price_type1`,
			`price_details`.`price_type2`
	)

create or replace view v_price_overview as
SELECT company_id,company_name,segment_id,dep_city,arv_city,flight_no,flight_date,dep_time,arv_time
,price_type1_alias
,min(price) as price
FROM
v_price_details
group by company_id,company_name,segment_id,dep_city,arv_city,flight_no,flight_date,dep_time,arv_time,price_type1_alias;