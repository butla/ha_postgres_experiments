FROM postgres:12.2

COPY pg_hba_fixer.sh /docker-entrypoint-initdb.d
