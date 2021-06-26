import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.core.s3_sync as s3
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse
from airflow_xtended_api.exceptions import (
    S3BucketDoesNotExistsError,
    S3ObjDownloadError,
    S3GenericError,
    OSFileHandlingError,
)


# decorator precedence matters... route should always be first
@blueprint.route("/s3_sync", methods=["POST"])
@csrf.exempt
@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG),
    ]
)
def sync_dags_from_s3():
    """Custom Function for the s3_sync API
    Sync DAG files from a S3 compatible storage backend.

    args:
        s3_bucket_name: s3 bucket name where the DAG files exist
        s3_region: s3 region name where the specified bucket exists
        s3_access_key: IAM entity access key having atleast S3 bucket read access
        s3_secret_key: IAM secret key for the specifed access key
        s3_object_prefix: filter s3 objects based on provided prefix
        s3_object_keys: sync DAG files specified by the object keys
        skip_purge: skip deleting existing files in the DAG folder
        otf_sync: sync dags in foreground
    """

    logging.info("Executing custom 'sync_dags_from_s3' function")

    s3_bucket_name = request.form.get("s3_bucket_name")
    if s3_bucket_name is None:
        return ApiResponse.bad_request("s3_bucket_name is required")

    s3_region = request.form.get("s3_region")
    if s3_region is None:
        return ApiResponse.bad_request("s3_region is required")

    s3_access_key = request.form.get("s3_access_key")
    if s3_access_key is None:
        return ApiResponse.bad_request("s3_access_key is required")

    s3_secret_key = request.form.get("s3_secret_key")
    if s3_secret_key is None:
        return ApiResponse.bad_request("s3_secret_key is required")

    obj_prefix = request.form.get("s3_object_prefix")
    if not obj_prefix:
        obj_prefix = ""

    # comma seperated obj keys as string
    obj_keys = request.form.get("s3_object_keys")

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
        s3.init_client(s3_access_key, s3_secret_key, s3_region)
        if obj_keys:
            obj_keys = obj_keys.strip().split(",")
            sync_status = s3.sync_specific_objects_from_bucket(
                s3_bucket_name, obj_keys, dag_utils.get_dag_folder()
            )
        else:
            sync_status = s3.sync_files_from_bucket(
                s3_bucket_name, dag_utils.get_dag_folder(), obj_prefix
            )
    except Exception as e:
        logging.exception("unable to complete sync from s3!!")
        if hasattr(e, "message"):
            return ApiResponse.other_error(e.message)
        return ApiResponse.other_error("unable to handle this request at this moment!!")

    dag_utils.scan_dags(otf_sync)

    return ApiResponse.success(
        {"message": "dag files synced from s3", "sync_status": sync_status}
    )
