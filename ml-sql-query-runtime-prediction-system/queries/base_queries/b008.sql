SELECT *
            FROM (
                SELECT
                    o_orderkey,
                    o_custkey,
                    o_totalprice,
                    ROW_NUMBER() OVER (PARTITION BY o_custkey ORDER BY o_totalprice DESC) AS rn
                FROM orders
            ) ranked
            WHERE rn <= 3
            LIMIT 200
