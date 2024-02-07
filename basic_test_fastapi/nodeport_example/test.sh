ADDR_PORT="192.168.1.55:30050"

for i in $(seq 1 10); do
    curl -L $ADDR_PORT
    echo " "
done