SELECT s.s_suppkey, s.s_name, n.n_name, r.r_name
            FROM supplier s
            JOIN nation n ON s.s_nationkey = n.n_nationkey
            JOIN region r ON n.n_regionkey = r.r_regionkey
            WHERE r.r_name IN ('ASIA', 'EUROPE')
            ORDER BY s.s_acctbal DESC
            LIMIT 100
