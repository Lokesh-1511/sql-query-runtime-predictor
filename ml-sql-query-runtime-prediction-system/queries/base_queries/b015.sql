SELECT o_orderkey, o_custkey, o_totalprice, o_orderdate
                FROM orders
                WHERE o_orderdate >= DATE '1997-01-01' AND o_totalprice > 175000
                ORDER BY o_totalprice DESC
                LIMIT 80
