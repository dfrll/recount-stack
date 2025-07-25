#! /usr/bin/env python3
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from pyrecount.accessor import Metadata
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path="/run/secrets/loader")

user = quote_plus(os.getenv("DB_USER"))
password = quote_plus(os.getenv("DB_PASS"))
dbname = quote_plus(os.getenv("DB_NAME"))
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

logger.info(f"Connecting to database '{dbname}' at {host}:{port} as user '{user}'")

uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(uri, echo=False, future=True)

organism = "human"
dbase = "sra"

# recount3 metadata
recount_metadata = Metadata(organism=organism)

recount_metadata.cache()

recount_meta_dataframe = recount_metadata.load().rename({"project": "project_id"})

recount_meta_dataframe.to_pandas().to_sql(
    "metadata", engine, if_exists="replace", index=False
)
