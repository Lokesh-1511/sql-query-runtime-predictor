SELECT c.c_custkey, c.c_name, o.o_orderkey, o.o_orderdate, o.o_totalprice
            FROM customer c
            JOIN orders o ON c.c_custkey = o.o_custkey
            WHERE o.o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1995-12-31'
            ORDER BY o.o_totalprice DESC
            LIMIT 100
