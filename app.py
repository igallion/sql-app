import pyodbc
import os
import time
from fastapi import FastAPI, Response, status, HTTPException
import hvac
import logging
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app
import time
import ssl
import yaml

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#Connects to SQL DB and retrieves information from location table
def connect_sql(USERNAME, PASSWORD, SERVER, DATABASE):
    logger.info("Connecting to database with credentials:")
    logger.info(f"Database Server {SERVER}:{DATABASE}")
    logger.info(f"Username: {USERNAME} - Password: {PASSWORD}")

    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};DATABASE={DATABASE};SERVER={SERVER};UID={USERNAME};PWD={PASSWORD};Encrypt=no'
    logger.info(f"Connection String: {connectionString}")
    start_time = time.time()
    try:
        conn = pyodbc.connect(connectionString)
        cursor = conn.cursor()
        SQL_QUERY = "SELECT * FROM location"
        logger.info(f"Running query: {SQL_QUERY}")
        cursor.execute(SQL_QUERY)
        resp = cursor.fetchall()

        logger.info("Closing connection to database")
        cursor.close()
        conn.close()
    finally:
        end_time = time.time()
        duration = end_time - start_time
        SQL_REQUEST_LATENCY.labels(operation='read', table='location').observe(duration)
    return resp

#Main SQL app
def sql_app():
    logger.info("Requesting database credentials from Vault")
    creds = vault_client.secrets.database.generate_credentials(
        name = config['vault']['VAULT_DB_ROLE'],
        mount_point = config['vault']['VAULT_DB_MOUNT_POINT']
    )
    
    logger.info("Requesting DB Server and Database name from Vault")
    dbInfo = vault_client.secrets.kv.v1.read_secret(
        path = config['vault']['VAULT_KV_SECRET_DB_INFO'],
        mount_point = config['vault']['VAULT_KV_MOUNT_POINT']
    )
    logger.info(f"DB info: Server {dbInfo['data']['db_server']} Database Name: {dbInfo['data']['db_database']}")

    logger.info("######### Connection #############")
    try:
        resp1 = connect_sql(creds['data']['username'], creds['data']['password'], dbInfo['data']['db_server'], dbInfo['data']['db_database'])
    except pyodbc.InterfaceError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
    return resp1

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

logger.info("Initializing FastAPI app")

app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

#Initialize Prometheus metrics
REQUEST_COUNTER = Counter(
    "app_requests_total",
    "Total number of requests to the app",
    ["endpoint"]
)

SQL_REQUEST_LATENCY = Histogram(
    'db_request_latency_seconds',
    'Database request latency in seconds',
    ['operation', 'table']
)

#Define api routes
@app.get("/")
def read_root():
    REQUEST_COUNTER.labels(endpoint="/").inc()
    logger.info("Returning message")
    return {"Message": "Hello World"}

@app.get("/sql-app", status_code=200)
def get_sql_app(response: Response):
    REQUEST_COUNTER.labels(endpoint='/sql-app').inc()
    resp = sql_app()
    logger.info(f"Returning response: {resp}")
    return {"message": f"{resp}"}
