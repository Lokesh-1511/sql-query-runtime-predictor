SELECT o_orderkey, o_custkey, o_totalprice, o_orderdate
                FROM orders
                WHERE o_orderdate >= DATE '1996-01-01' AND o_totalprice > 170000
                ORDER BY o_totalprice DESC
                LIMIT 80
