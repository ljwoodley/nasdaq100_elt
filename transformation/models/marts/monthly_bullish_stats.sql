select
    session_month,
    session_month_name,
    round(100.0 * avg(case when return_percent > 0 then 1 else 0 end))
        as bullish_percentage
from {{ ref('monthly_performance') }}
group by session_month, session_month_name,
order by session_month
