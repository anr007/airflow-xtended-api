import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/scan_dags", methods=["GET"])
@csrf.exempt
@security.requires_access(
    [(permissions.ACTION_CAN_READ, permissions.RESOURCE_PERMISSION)]
)
def scan_dags():
    """Custom Function for the scan_dags API.
    Airflow 2.x can run multiple schedulers concurrently in an active / active model.
    As the dag parser code is tightly coupled as part of scheduler,
    It's better to create a new Scheduler job than to implement the dag parser logic.

    args:
        otf_syc: sync dags in foreground
    """
    otf_sync = request.args.get("otf_sync", None)
    dag_utils.scan_dags(otf_sync)
    return ApiResponse.success({"message": "Ondemand DAG scan complete!!"})
