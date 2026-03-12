SELECT c_custkey, c_name, c_phone, c_acctbal
            FROM customer
            WHERE c_acctbal BETWEEN 10000 AND 20000
            ORDER BY c_acctbal DESC
            LIMIT 100
