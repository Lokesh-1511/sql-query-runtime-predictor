SELECT
                COUNT(*) AS order_count,
                AVG(o_totalprice) AS avg_price,
                MAX(o_totalprice) AS max_price
            FROM orders
            WHERE o_totalprice > 10
