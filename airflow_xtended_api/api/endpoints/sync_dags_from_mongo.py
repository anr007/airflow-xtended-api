import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.core.mongo_sync as mongo
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse
from airflow_xtended_api.exceptions import MongoClientError, OSFileHandlingError

# decorator precedence matters... route should always be first
@blueprint.route("/mongo_sync", methods=["POST"])
@csrf.exempt
@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG),
    ]
)
def sync_dags_from_mongo():
    """Custom Function for the mongo_sync API
    Get serialized DAG code from mongo db and create local DAG files using the same.

    args:
        connection_string: mongo server connection string
        db_name: mongo database name where DAG data exists
        collection_name: mongodb collection where DAG data exists
        field_filename: mongo db document field referring DAG filenames
        field_dag_source: mongodb document field referring DAG python source
        query_filter: JSON query string to filter required documents
        skip_purge: skip deleting existing files in the DAG folder
        otf_sync: sync dags in foreground
    """

    logging.info("Executing custom 'sync_dags_from_mongo' function")

    conn_str = request.form.get("connection_string")
    if conn_str is None:
        return ApiResponse.bad_request("conn_str is required")

    db_name = request.form.get("db_name")
    if db_name is None:
        return ApiResponse.bad_request("db_name is required")

    coll_name = request.form.get("collection_name")
    if coll_name is None:
        return ApiResponse.bad_request("collection_name is required")

    attr_filename = request.form.get("field_filename")
    if attr_filename is None:
        return ApiResponse.bad_request("field_filename is required")

    attr_dag_source = request.form.get("field_dag_source")
    if attr_dag_source is None:
        return ApiResponse.bad_request("field_dag_source is required")

    query_filter = request.form.get("query_filter")

    skip_purge = request.form.get("skip_purge") is not None

    otf_sync = request.form.get("otf_sync") is not None
    logging.info("create_dag in sync state: " + str(otf_sync))

    if not skip_purge:
        try:
            dag_utils.empty_dag_folder()
        except Exception:
            logging.exception("error emptying dag folder... ")
    else:
        logging.warning("skipping: purge dag folder... ")

    sync_status = None
    try:
        mongo.init_client(conn_str, db_name)
        sync_status = mongo.sync_files_from_collection(
            db_name,
            coll_name,
            attr_filename,
            attr_dag_source,
            dag_utils.get_dag_folder(),
            query_filter,
        )
    except Exception as e:
        logging.exception("unable to complete sync from mongo!!")
        if hasattr(e, "message"):
            return ApiResponse.other_error(e.message)
        return ApiResponse.other_error("unable to handle this request at this moment!!")

    dag_utils.scan_dags(otf_sync)

    return ApiResponse.success(
        {"message": "dag files synced from mongo", "sync_status": sync_status}
    )
