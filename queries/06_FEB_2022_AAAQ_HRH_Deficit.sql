CREATE TEMP FUNCTION
  occupation_nco_1968(nco string)
  RETURNS string AS (
    CASE
      WHEN nco = '085' THEN 'ANM'
      WHEN nco = '084' THEN 'Nurse'
      WHEN nco = '076' THEN 'Pharmacist'
      WHEN nco = '083' THEN 'Pharmacist'
      WHEN nco = '070' THEN 'Doctor'
      WHEN nco = '078' THEN 'Doctor'
      WHEN nco = '079' THEN 'Doctor'
      WHEN nco = '074' THEN 'Dentist'
      WHEN nco = '081' THEN 'Dentist'
      WHEN nco = '071' THEN 'AYUSH'
      WHEN nco = '072' THEN 'AYUSH'
      WHEN nco = '073' THEN 'AYUSH'
    ELSE
    NULL
  END
    );
CREATE TEMP FUNCTION
  occupation_nco_2004(nco string)
  RETURNS string AS (
    CASE
      WHEN nco = '3232' THEN 'ANM'
      WHEN nco = '2230' THEN 'Nurse'
      WHEN nco = '3231' THEN 'Nurse'
      WHEN nco = '3228' THEN 'Pharmacist'
      WHEN nco = '2221' THEN 'Doctor'
      WHEN nco = '2225' THEN 'Dentist'
      WHEN nco = '3225' THEN 'Dentist'
      WHEN nco = '2222' THEN 'AYUSH'
      WHEN nco = '2223' THEN 'AYUSH'
      WHEN nco = '2224' THEN 'AYUSH'
    ELSE
    NULL
  END
    );

CREATE TEMP FUNCTION
  state_code_38(code string)
  RETURNS string AS (code);

CREATE TEMP FUNCTION
  state_code_50(code string)
  RETURNS string AS (code);

WITH
  workers_38 AS (
  SELECT
    ifnull( 
      occupation_nco_1968(B6_q6),
      occupation_nco_1968(B6_q11) ) AS occupation,
    Hhold_key AS hhid,
    Wgt4_pooled AS weight_,
    State AS state_
  FROM
    `asar-287123.nss.nss_38_block_6` ),

  households_38 AS (
  SELECT
    hhid,
    occupation,
    state_,
    COUNT(occupation) AS count_,
    ANY_VALUE(weight_) AS weight_,
  FROM
    workers_38
  WHERE
    occupation != 'Other'
  GROUP BY
    hhid,
    occupation,
    state_ ),

  estimates_38 AS (
  SELECT
    state_code_38(state_) AS state_,
    occupation,
    SUM(count_ * weight_) AS population_,
  FROM
    households_38
  GROUP BY
    occupation,
    state_ ),

  workers_50 AS (
  SELECT
    ifnull(
      occupation_nco_1968(B4_q15),
      occupation_nco_1968(B4_q21) ) AS occupation,
    Hhold_key AS hhid,
    Wgt4_pooled AS weight_,
    State AS state_
  FROM
    `asar-287123.nss.nss_50_block_4` ),

  households_50 AS (
  SELECT
    hhid,
    occupation,
    state_,
    COUNT(occupation) AS count_,
    ANY_VALUE(weight_) AS weight_,
  FROM
    workers_50
  WHERE
    occupation != 'Other'
  GROUP BY
    hhid,
    occupation,
    state_ ),

  estimates_50 AS (
  SELECT
    state_code_50(state_) AS state_,
    occupation,
    SUM(count_ * weight_) AS population_,
  FROM
    households_50
  GROUP BY
    occupation,
    state_ ),

  workers_main_55 AS (
  SELECT
    ifnull(
      occupation_nco_1968(B51_q6),
      occupation_nco_1968(B4_q21) ) AS occupation,
    Key_Hhold AS hhid,
    Wgt4_pooled AS weight_,
    State AS state_
  FROM
    `asar-287123.nss.nss_55_block_511` as b51
  OUTER JOIN
    `asar-287123.nss.nss_55_block_521` as b52
  ON
    b51.Key_Hhold = b52.Key_Hhold AND
    b51.Key_prsn = b52.Key_prsn
    ),

  workers_sub_55 AS (
    SELECT
      occupation_nco_1968(B52_q6) AS occupation,

  ),

  households_55 AS (
  SELECT
    hhid,
    occupation,
    state_,
    COUNT(occupation) AS count_,
    ANY_VALUE(weight_) AS weight_,
  FROM
    workers_55
  WHERE
    occupation != 'Other'
  GROUP BY
    hhid,
    occupation,
    state_ ),

  estimates_55 AS (
  SELECT
    state_code_55(state_) AS state_,
    occupation,
    SUM(count_ * weight_) AS population_,
  FROM
    households_55
  GROUP BY
    occupation,
    state_ )

SELECT
  state_,
  occupation,
  population_
FROM
  estimates_38;