import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/purge_dags", methods=["GET"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG)])
def purge_dags():
    """Custom Function for the purge_dags API
    Delete all files in the DAG folder
    """

    try:
        dag_utils.empty_dag_folder()
    except Exception:
        logging.exception("error emptying dag folder... ")
        return ApiResponse.other_error("unable to purge dags!!")
    return ApiResponse.success({"message": "DAG directory purged!!"})
