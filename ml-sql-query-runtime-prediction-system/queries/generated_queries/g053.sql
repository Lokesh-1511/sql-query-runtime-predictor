SELECT o.o_orderkey, o.o_orderdate, l.l_partkey, l.l_extendedprice
            FROM orders o
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            WHERE l.l_discount > 0.07
            ORDER BY l.l_extendedprice DESC
            LIMIT 120
