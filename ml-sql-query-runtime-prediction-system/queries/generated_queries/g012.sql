SELECT o_orderkey, o_custkey, o_totalprice, o_orderdate
                    FROM orders
                    WHERE o_totalprice > 1000
                    ORDER BY o_totalprice DESC
                    LIMIT 100
