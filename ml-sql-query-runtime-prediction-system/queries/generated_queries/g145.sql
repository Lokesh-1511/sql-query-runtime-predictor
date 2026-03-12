SELECT *
            FROM (
                SELECT
                    o_orderkey,
                    o_custkey,
                    o_totalprice,
                    DENSE_RANK() OVER (PARTITION BY o_orderpriority ORDER BY o_totalprice DESC) AS price_rank
                FROM orders
                WHERE o_totalprice > 5000
            ) t
            WHERE price_rank <= 5
            LIMIT 150
