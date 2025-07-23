import uvicorn
import hvac
import os
import logging
import yaml

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.info("Loading config")
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

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
    mount_point=config['vault']['VAULT_PKI_MOUNT_POINT'],
    name=config['vault']['VAULT_PKI_ROLE'],
    common_name="sql-app",
    extra_params={'alt_names': 'localhost'}
)

with open('cert.cer', 'w') as f:
    f.write(vault_cert_request['data']['certificate'])

with open('cert.key', 'w') as f:
    f.write(vault_cert_request['data']['private_key'])

uvicorn.run("app:app", port=443, host='0.0.0.0', ssl_keyfile='cert.key', ssl_certfile='cert.cer')