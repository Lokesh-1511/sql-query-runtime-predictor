SELECT o_orderkey, o_custkey, o_totalprice, o_orderdate
                    FROM orders
                    WHERE o_totalprice > 50
                    ORDER BY o_totalprice DESC
                    LIMIT 100
