import logging
import os

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf
from airflow.models import DagModel
from airflow import settings
from airflow.api.common.experimental import delete_dag as exp_delete_dag

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse

from airflow_xtended_api.exceptions import (
    DagDoesNotExistsError,
    OSFileHandlingError,
)

# response keys
MSG = "success_message"
ERR = "error_message"


@blueprint.route("/delete_dag", methods=["GET"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG)])
def delete_dag():
    """Custom Function for the delete_dag API.
    Delete dag having the specified dag id and also delete the associated dag file

    args:
        dag_id: dag id
        filename: name of a DAG file
    """
    logging.info("Executing custom 'delete_dag' function")

    dag_id = request.args.get("dag_id", None)
    logging.info(f"dag_id to delete: '{dag_id}'")

    dag_filename = request.args.get("filename", None)
    logging.info(f"dag_id to delete: '{dag_filename}'")

    if dag_id is None and dag_filename is None:
        return ApiResponse.bad_request("dag_id or filename is required")

    if dag_id:
        dag_id_resp = {MSG: None, ERR: None}
        try:
            del_dag(dag_id)
            dag_id_resp[MSG] = f"DAG [{dag_id}] deleted"
        except Exception as e:
            dag_id_resp[ERR] = getattr(e, "message", repr(e))

    if dag_filename:
        dag_filename_resp = {MSG: None, ERR: None}
        try:
            del_file(dag_filename)
            dag_filename_resp[MSG] = f"{dag_filename} deleted"
        except Exception as e:
            dag_filename_resp[ERR] = getattr(e, "message", repr(e))

    if dag_id and dag_filename:
        if dag_id_resp[ERR] and dag_filename_resp[ERR]:
            return ApiResponse.other_error(
                {
                    "dag_id": dag_id_resp[ERR],
                    "filename": dag_filename_resp[ERR],
                }
            )
        return ApiResponse.success(
            {
                "message": {
                    "dag_id": filter_resp(dag_id_resp),
                    "filename": filter_resp(dag_filename_resp),
                }
            }
        )

    if dag_id:
        if not dag_id_resp[ERR]:
            return ApiResponse.success({"message": dag_id_resp[MSG]})
        return ApiResponse.other_error(dag_id_resp[ERR])

    if dag_filename:
        if not dag_filename_resp[ERR]:
            return ApiResponse.success({"message": dag_filename_resp[MSG]})
        return ApiResponse.other_error(dag_filename_resp[ERR])


def del_dag(dag_id):
    dag_id = dag_id.strip()

    if not dag_utils.check_dag_exists(dag_id):
        msg = f"The DAG ID '{dag_id}' does not exist"
        logging.error(msg)
        raise DagDoesNotExistsError(msg)

    try:
        dag_full_path = os.path.join(dag_utils.get_dag_folder(), f"{dag_id}.py")

        if os.path.exists(dag_full_path):
            os.remove(dag_full_path)

        deleted_dags = exp_delete_dag.delete_dag(dag_id, keep_records_in_log=False)

        if deleted_dags > 0:
            logging.info("Deleted dag " + dag_id)
        else:
            logging.info("No dags deleted")
    except Exception as e:
        msg = f"An error occurred while trying to delete the DAG '{dag_id}':{repr(e)}"
        logging.exception(msg)
        raise OSFileHandlingError(msg)


def del_file(dag_filename):
    try:
        dag_filename = dag_filename.strip().split(os.sep)[-1]
        dag_full_path = os.path.join(dag_utils.get_dag_folder(), dag_filename)
        os.remove(dag_full_path)
    except Exception as e:
        msg = f"unable to delete '{dag_filename}': {repr(e)}"
        logging.exception(msg)
        raise OSFileHandlingError(msg)


def filter_resp(response):
    return response[ERR] if response[ERR] else response[MSG]
