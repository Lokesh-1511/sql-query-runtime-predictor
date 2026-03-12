SELECT o_orderpriority, COUNT(*) AS order_count
            FROM orders
            GROUP BY o_orderpriority
            ORDER BY order_count DESC
