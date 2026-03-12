SELECT o_orderkey, o_orderdate, o_totalprice
            FROM orders
            WHERE o_totalprice > 250000
            ORDER BY o_totalprice DESC
            LIMIT 100
