import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow import settings
from airflow.www.app import csrf
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils import timezone
from airflow.exceptions import TaskNotFound

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/skip_task_instance", methods=["GET"])
@csrf.exempt
@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
    ]
)
def skip_task_instance():
    """Skip the specified task instance and downstream tasks.
    Obtain task instance from session according to dag_id, run_id and task_id,
    define the state of this task instance as SKIPPED.

    args:
        dag_id: dag id
        run_id: the run id of dag run
        task_id: the task id of task instance of dag
    """
    logging.info("Executing custom 'skip_task_instance' function")

    dag_id = request.args.get("dag_id", None)
    if dag_id is None:
        return ApiResponse.bad_request("DAG id is required")
    run_id = request.args.get("run_id", None)
    if run_id is None:
        return ApiResponse.bad_request("Run id is required")
    task_id = request.args.get("task_id", None)
    if task_id is None:
        return ApiResponse.bad_request("Task id is required")

    dag_id = dag_id.strip()
    run_id = run_id.strip()
    task_id = task_id.strip()

    if not dag_utils.check_dag_exists(dag_id):
        return ApiResponse.bad_request(
            "The DAG ID '" + str(dag_id) + "' does not exist"
        )

    session = settings.Session()
    query = session.query(DagRun)
    dag_run = query.filter(DagRun.dag_id == dag_id, DagRun.run_id == run_id).first()

    if dag_run is None:
        return ApiResponse.not_found("dag run is not found")

    logging.info("dag_run：" + str(dag_run))

    task_instance = DagRun.get_task_instance(dag_run, task_id)

    if task_instance is None:
        return ApiResponse.not_found("dag task is not found")

    logging.info("task_instance：" + str(task_instance))

    task_instance.state = State.SKIPPED
    session.merge(task_instance)
    session.commit()
    session.close()

    return ApiResponse.success({"message": f"{str(task_instance)} skipped!!"})
