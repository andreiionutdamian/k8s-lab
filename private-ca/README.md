# Create a private Certificare Authority

## Prereuisites 
Make sure you have openssl installed on your system

```bash
sudo apt-get install openssl
```

## Create private key for CA
```bash
openssl genrsa -out myCA.key 2048
```

## Create a Self-Signed Root Certificate
```bash
openssl req -x509 -new -nodes -key myCA.key -sha256 -days 3650 -out myCA.crt
```

## Install CA on client machines
* Copy the certificate `myCA.crt` to the target machine 
* Update machine ca-certs

```bash
sudo cp /tmp/myCA.crt /usr/local/share/ca-certificates/
```

For Ubuntu linux follow the above step to ensure the Root CA will be used to validate certificates signed by this CA.
it is mandatory that the certificate is copyed in this location `/usr/local/share/ca-certificates/`


```bash
sudo update-ca-certificates
```

# Create your first self-signed certificate
1. Generate a private key 
```bash
openssl genrsa -out service.key 2048
```

2. Create a Certificate Signing Request (CSR)
```bash
openssl req -new -key service.key -out service.csr
```

3. Sign the CSR with Your CA
```bash
openssl x509 -req -in service.csr -CA /root/ca/certs/myCA.crt -CAkey /root/ca/private/myCA.key -CAcreateserial -out service.crt -days 365 -sha256
```

