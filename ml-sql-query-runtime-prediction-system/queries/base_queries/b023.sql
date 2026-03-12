SELECT *
                FROM (
                    SELECT
                        l_partkey,
                        l_shipdate,
                        l_extendedprice,
                        AVG(l_extendedprice) OVER (
                            PARTITION BY l_partkey
                            ORDER BY l_shipdate
                            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
                        ) AS moving_avg_price
                    FROM lineitem
                    WHERE EXTRACT(MONTH FROM l_shipdate) = 7
                ) t
                LIMIT 120
