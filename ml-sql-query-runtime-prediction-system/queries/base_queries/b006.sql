SELECT
                AVG(l_quantity) AS avg_qty,
                AVG(l_discount) AS avg_discount,
                SUM(l_extendedprice) AS total_extendedprice
            FROM lineitem
            WHERE l_shipdate BETWEEN DATE '1994-01-01' AND DATE '1996-12-31'
