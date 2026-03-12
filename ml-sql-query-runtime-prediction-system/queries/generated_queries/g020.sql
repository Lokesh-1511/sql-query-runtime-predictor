SELECT l_orderkey, l_partkey, l_quantity, l_extendedprice
                    FROM lineitem
                    WHERE l_quantity > 5000
                    ORDER BY l_extendedprice DESC
                    LIMIT 100
