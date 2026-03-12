SELECT l_returnflag, COUNT(*) AS cnt, SUM(l_extendedprice) AS total_price
                FROM lineitem
                GROUP BY l_returnflag
                ORDER BY total_price DESC
