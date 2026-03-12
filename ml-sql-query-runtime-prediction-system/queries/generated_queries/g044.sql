SELECT c.c_custkey, c.c_name, o.o_orderkey, o.o_totalprice
            FROM customer c
            JOIN orders o ON c.c_custkey = o.o_custkey
            WHERE o.o_totalprice > 0.03
            ORDER BY o.o_totalprice DESC
            LIMIT 120
