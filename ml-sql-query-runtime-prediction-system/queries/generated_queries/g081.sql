SELECT
                SUM(l_extendedprice) AS total_price,
                AVG(l_discount) AS avg_discount,
                SUM(l_quantity) AS total_qty
            FROM lineitem
            WHERE l_quantity > 20
