ADDR_PORT="192.168.1.54/pg_test"

for i in $(seq 1 10); do
    curl -L $ADDR_PORT
    echo " "
done

curl -s $ADDR_PORT/stats | jq .