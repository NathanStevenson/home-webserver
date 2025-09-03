
git init
python3 -m venv venv
$(pwd)/venv/bin/pip install -r $(pwd)/quart_project/requirements.txt
openssl req -x509 -newkey rsa:4096 -keyout priv_key.pem -out pub_cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"
mv $(pwd)/priv_key.pem $(pwd)/quart_project/secrets/
mv $(pwd)/pub_cert.pem $(pwd)/quart_project/secrets/