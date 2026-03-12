SELECT l_shipinstruct, COUNT(*) AS cnt, SUM(l_extendedprice) AS total_price
                FROM lineitem
                GROUP BY l_shipinstruct
                ORDER BY total_price DESC
