curl --location 'http://192.168.1.51:30050/predict/' \
--header 'Content-Type: application/json' \
--data "{
  \"text\": \"$1\"
}"
