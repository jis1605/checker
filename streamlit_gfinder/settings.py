from dotenv import load_dotenv
from os.path import join, dirname
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)

DEV_ELASTIC_ENDPOINT = os.environ.get("DEV_ELASTIC_ENDPOINT")
DEV_ELASTIC_USER_ID = os.environ.get("DEV_ELASTIC_USER_ID")
DEV_ELASTIC_PASSWORD = os.environ.get("DEV_ELASTIC_PASSWORD")

PROD_ELASTIC_ENDPOINT = os.environ.get("PROD_ELASTIC_ENDPOINT")
PROD_ELASTIC_USER_ID = os.environ.get("PROD_ELASTIC_USER_ID")
PROD_ELASTIC_PASSWORD = os.environ.get("PROD_ELASTIC_PASSWORD")