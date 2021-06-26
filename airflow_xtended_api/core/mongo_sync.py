import os
import logging
import json
from concurrent import futures

from pymongo import MongoClient

from airflow_xtended_api.exceptions import (
    MongoClientError,
    OSFileHandlingError,
)

mongo = None
MAX_IO_THREADS = 5


def init_client(conn_str, db_name):
    global mongo
    if not mongo:
        mongo = MongoClient(conn_str)
        db = mongo[db_name]
        try:
            db.command("serverStatus")
        except Exception as e:
            raise MongoClientError("Unable to reach Mongo server", repr(e))
        else:
            logging.info("MongoDB connection established")

    return mongo


def sync_files_from_collection(
    db_name,
    collection_name,
    attr_filename,
    attr_dag_source,
    sync_dir,
    query_filter=None,
):
    global mongo
    db = mongo[db_name]
    coll = db[collection_name]

    try:
        query_filter = json.loads(query_filter)
        cur = coll.find(filter=query_filter)
    except Exception:
        logging.exception(f"unable to parse query_filter: {query_filter}, ignored")
        cur = coll.find()

    documents = []
    for doc in cur:
        try:
            filename = doc[attr_filename]
            dag_source = doc[attr_dag_source]
            documents.append([filename, dag_source])
        except KeyError:
            logging.error("unable to parse a document...")

    sync_status = {"synced": [], "failed": []}
    for filename, download_result in generate_dags(documents, sync_dir):
        if type(download_result) is bool:
            sync_status["synced"].append(filename)
        else:
            sync_status["failed"].append(f"{filename}: {repr(download_result)}")
    logging.info(sync_status)
    return sync_status


def generate_dags(documents, sync_dir):
    with futures.ThreadPoolExecutor(max_workers=MAX_IO_THREADS) as executor:
        # dict of future, filename
        future_2_filename_map = {
            executor.submit(create_dag_file, doc[0], doc[1], sync_dir): doc[0]
            for doc in documents
        }

        for future in futures.as_completed(future_2_filename_map):
            filename = future_2_filename_map[future]
            exception = future.exception()
            if not exception:
                yield filename, future.result()
            else:
                yield filename, exception


def create_dag_file(filename, dag_source, sync_dir):
    if not filename.split(".")[-1] in ["py", "pyc"]:
        filename = f"{filename}.py"

    try:
        dag_file = os.path.join(sync_dir, filename)
        with open(dag_file, "w") as fd:
            fd.write(dag_source)
            fd.close()
    except OSError:
        raise OSFileHandlingError(f"unable to write {filename}")

    return True
