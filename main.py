import uvicorn
import hvac
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.info("Initializing Vault connection")
#Initialize connection to Vault
VAULT_ADDR = os.getenv('VAULT_ADDR')
VAULT_USER = os.getenv('VAULT_USER')
VAULT_PASS = os.getenv('VAULT_PASS')

vault_client = hvac.Client(
    url = VAULT_ADDR
)

vault_client.auth.userpass.login(
    username = VAULT_USER,
    password = VAULT_PASS
)

vault_cert_request = vault_client.secrets.pki.generate_certificate(
    mount_point='pki_int',
    name="sql-app",
    common_name="sql-app",
    extra_params={'alt_names': 'localhost'}
)

with open('cert.cer', 'w') as f:
    f.write(vault_cert_request['data']['certificate'])

with open('cert.key', 'w') as f:
    f.write(vault_cert_request['data']['private_key'])

uvicorn.run("app:app", port=443, host='0.0.0.0', ssl_keyfile='cert.key', ssl_certfile='cert.cer')