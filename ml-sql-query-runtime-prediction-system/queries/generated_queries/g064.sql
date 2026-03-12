SELECT s.s_name, n.n_name, r.r_name, s.s_acctbal
            FROM supplier s
            JOIN nation n ON s.s_nationkey = n.n_nationkey
            JOIN region r ON n.n_regionkey = r.r_regionkey
            WHERE s.s_acctbal > 0.01
            ORDER BY s.s_acctbal DESC
            LIMIT 120
