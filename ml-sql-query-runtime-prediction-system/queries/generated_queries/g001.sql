SELECT c_custkey, c_name, c_acctbal
                    FROM customer
                    WHERE c_acctbal > 10
                    ORDER BY c_acctbal DESC
                    LIMIT 100
