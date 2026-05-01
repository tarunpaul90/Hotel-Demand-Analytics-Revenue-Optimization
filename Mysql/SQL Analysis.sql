-- Query 8 — Executive Summary View (Board Report)

-- Business Question: What is the overall performance of each hotel across key revenue KPIs?
-- Objective: Provide a single-row-per-hotel KPI summary for executive decision-making dashboards.

WITH base AS (
    SELECT 
        hotel,
        adr,

        CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END AS occupied,

        CASE 
            WHEN distribution_channel IN ('TA/TO','GDS') THEN 0.15
            ELSE 0
        END AS commission_rate

    FROM hotel_bookings
),

agg AS (
    SELECT 
        hotel,

        COUNT(*) AS total_bookings,

        ROUND(AVG(adr), 2) AS ADR,

        ROUND(AVG(occupied), 2) AS Occupancy,

        ROUND(AVG(adr) * AVG(occupied), 2) AS RevPAR,

        -- Revenue
        ROUND(SUM(adr), 2) AS total_revenue,

        -- Commission loss
        ROUND(SUM(adr * commission_rate), 2) AS commission_cost,

        -- Operating cost (assumption: 40%)
        ROUND(SUM(adr) * 0.40, 2) AS operating_cost

    FROM base
    GROUP BY hotel
)

SELECT 
    hotel,

    total_bookings,

    ADR,
    Occupancy,
    RevPAR,

    total_revenue,
    commission_cost,
    operating_cost,

    -- Net Profit
    ROUND(
        total_revenue - commission_cost - operating_cost,
    2) AS net_profit,

    -- Profit Margin %
    ROUND(
        (total_revenue - commission_cost - operating_cost) 
        / total_revenue * 100,
    2) AS profit_margin_percent

FROM agg
ORDER BY net_profit DESC;