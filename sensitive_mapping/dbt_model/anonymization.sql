{{ config(materialized='table') }}


SELECT
    1 AS id,
    'Alice' AS name,
    DATE '1993-04-12' AS dob,
    32 AS age,
    '32' AS age_str,
    'W1A 1AA' AS postcode
