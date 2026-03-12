SELECT o.o_orderkey, o.o_orderpriority, l.l_linenumber, l.l_extendedprice
            FROM orders o
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            WHERE l.l_discount > 0.05
            ORDER BY l.l_extendedprice DESC
            LIMIT 100
