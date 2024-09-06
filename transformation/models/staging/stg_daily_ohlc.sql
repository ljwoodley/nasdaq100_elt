with
source as (
    select * from {{ source('yfinance','nasdaq100_daily_ohlc') }}
),

final as (
    select
        open,
        high,
        low,
        close,
        cast(date as date) as session_date,
        extract(year from date) as session_year,
        extract(month from date) as session_month,
        strftime('%B', date) as session_month_name,
        case
            when
                extract(week from date) = 1 and extract(month from date) = 12
                then 52
            when extract(week from date) = 53 then 52
            else extract(week from date)
        end as session_week_of_year
    from source
    order by session_date
)

select * from final
