SELECT l_orderkey, l_partkey, l_quantity, l_extendedprice
            FROM lineitem
            WHERE l_shipdate >= DATE '1997-01-01'
            ORDER BY l_extendedprice DESC
            LIMIT 100
