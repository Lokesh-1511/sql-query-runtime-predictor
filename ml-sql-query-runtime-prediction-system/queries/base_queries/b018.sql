SELECT l_shipmode, COUNT(*) AS cnt, SUM(l_extendedprice) AS total_price
                FROM lineitem
                GROUP BY l_shipmode
                ORDER BY total_price DESC
