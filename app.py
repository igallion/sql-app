import pyodbc
import os
import time
from fastapi import FastAPI, Response, status, HTTPException
import hvac
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#Connects to SQL DB and retrieves information from location table
def connect_sql(USERNAME, PASSWORD, SERVER, DATABASE):
    logger.info("Connecting to database with credentials:")
    logger.info(f"Database Server {SERVER}:{DATABASE}")
    logger.info(f"Username: {USERNAME} - Password: {PASSWORD}")

    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};DATABASE={DATABASE};SERVER={SERVER};UID={USERNAME};PWD={PASSWORD};Encrypt=no'
    logger.info(f"Connection String: {connectionString}")
    conn = pyodbc.connect(connectionString)
    cursor = conn.cursor()
    SQL_QUERY = "SELECT * FROM location"
    logger.info(f"Running query: {SQL_QUERY}")
    cursor.execute(SQL_QUERY)
    resp = cursor.fetchall()

    logger.info("Closing connection to database")
    cursor.close()
    conn.close()
    return resp

#Main SQL app
def sql_app():
    roleName = "mssql-role"
    db_mount_point = 'database'
    logger.info("Requesting database credentials from Vault")
    creds = vault_client.secrets.database.generate_credentials(
        name = roleName,
        mount_point = db_mount_point
    )
    
    logger.info("Requesting DB Server and Database name from Vault")
    dbInfo = vault_client.secrets.kv.v1.read_secret(
        path = 'sql-app/dev/dbinfo',
        mount_point = 'BusinessUnit1'
    )
    logger.info(f"DB info: Server {dbInfo['data']['db_server']} Database Name: {dbInfo['data']['db_database']}")

    logger.info("######### Connection #############")
    try:
        resp1 = connect_sql(creds['data']['username'], creds['data']['password'], dbInfo['data']['db_server'], dbInfo['data']['db_database'])
    except pyodbc.InterfaceError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
    return resp1

app = FastAPI()

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

#Define api routes
@app.get("/")
def read_root():
    logger.info("Returning message")
    return {"Message": "Hello World"}

@app.get("/sql-app", status_code=200)
def get_sql_app(response: Response):
    resp = sql_app()
    logger.info(f"Returning response: {resp}")
    return {"message": f"{resp}"}

@app.get("/metrics")
def get_metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}