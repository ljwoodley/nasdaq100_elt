{% macro calculate_session_returns(time_unit) %}

    with daily_ohlc as (
        select * from {{ ref('stg_daily_ohlc') }}
    ),
    
    session_period as (
        select
            session_year,
            {% if time_unit == 'week' %}
                session_week_of_year as time_unit,
            {% elif time_unit == 'month' %}
                session_month as time_unit,
                session_month_name,
            {% endif %}
            min(session_date) as start_date,
            max(session_date) as end_date
        from daily_ohlc
        group by all
    ),
    
    final as (
        select
            session_period.session_year,
            {% if time_unit == 'week' %}
                session_period.time_unit as session_week_of_year,
            {% elif time_unit == 'month' %}
                session_period.time_unit as session_month,
                session_period.session_month_name,
            {% endif %}
            min(case when daily_ohlc.session_date = session_period.start_date then open end) as open,
            max(daily_ohlc.high) as high,
            min(daily_ohlc.low) as low,
            max(case when daily_ohlc.session_date = session_period.end_date then close end) as close
        from session_period
        join daily_ohlc on daily_ohlc.session_date = session_period.start_date
                        or daily_ohlc.session_date = session_period.end_date
        group by all
    )
    
    select
        *,
        (close - open) / open * 100 as return_percent
    from final
{% endmacro %}
