SELECT c_custkey, c_name, c_phone, c_acctbal
            FROM customer
            WHERE c_acctbal BETWEEN 0 AND 500
            ORDER BY c_acctbal DESC
            LIMIT 100
