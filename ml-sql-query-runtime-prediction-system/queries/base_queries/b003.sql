SELECT c_custkey, c_name, c_mktsegment, c_acctbal
            FROM customer
            WHERE c_mktsegment IN ('BUILDING', 'AUTOMOBILE') AND c_acctbal > 1000
            ORDER BY c_acctbal DESC
            LIMIT 100
