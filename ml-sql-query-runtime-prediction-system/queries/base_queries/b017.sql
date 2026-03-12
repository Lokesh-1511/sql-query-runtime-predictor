SELECT l_linestatus, COUNT(*) AS cnt, SUM(l_extendedprice) AS total_price
                FROM lineitem
                GROUP BY l_linestatus
                ORDER BY total_price DESC
