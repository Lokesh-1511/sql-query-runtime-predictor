SELECT o_orderpriority, COUNT(*) AS cnt, AVG(o_totalprice) AS avg_price
            FROM orders
            WHERE o_totalprice > 10000
            GROUP BY o_orderpriority
            ORDER BY cnt DESC
