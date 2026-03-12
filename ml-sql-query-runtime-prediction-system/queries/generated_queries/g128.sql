SELECT c_custkey, c_name, c_phone, c_acctbal
            FROM customer
            WHERE c_acctbal BETWEEN 2000 AND 5000
            ORDER BY c_acctbal DESC
            LIMIT 100
