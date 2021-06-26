import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow import settings
from airflow.www.app import csrf
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils import timezone

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/kill_running_tasks", methods=["GET"])
@csrf.exempt
@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
    ]
)
def kill_running_tasks():
    """Stop running the specified task instance and downstream tasks.
    Obtain task_instance from session according to dag_id, run_id and task_id,
    If task_id is not empty, get task_instance with RUNNING or NONE status from dag_run according to task_id,
        and set task_instance status to FAILED.
    If task_id is empty, get all task_instances whose status is RUNNING or NONE from dag_run,
        and set the status of these task_instances to FAILED.

    args:
        dag_id: dag id
        run_id: the run id of dag run
        task_id: the task id of task instance of dag
    """

    logging.info("Executing custom 'kill_running_tasks' function")

    dag_id = request.args.get("dag_id", None)
    if dag_id is None:
        return ApiResponse.bad_request("DAG id is required")
    run_id = request.args.get("run_id", None)
    if run_id is None:
        return ApiResponse.bad_request("Run id is required")
    task_id = request.args.get("task_id", None)

    dag_id = dag_id.strip()
    run_id = run_id.strip()

    if not dag_utils.check_dag_exists(dag_id):
        return ApiResponse.bad_request(
            "The DAG ID '" + str(dag_id) + "' does not exist"
        )

    dagbag = dag_utils.get_dagbag()

    session = settings.Session()
    query = session.query(DagRun)
    dag_run = query.filter(DagRun.dag_id == dag_id, DagRun.run_id == run_id).first()

    if dag_run is None:
        return ApiResponse.not_found("dag run is not found")

    if dag_id not in dagbag.dags:
        return ApiResponse.bad_request("Dag id {} not found".format(dag_id))

    dag = dagbag.get_dag(dag_id)
    logging.info("dag: " + str(dag))
    logging.info("dag_subdag: " + str(dag.subdags))

    tis = []
    if task_id:
        task_id = task_id.strip()
        task_instance = DagRun.get_task_instance(dag_run, task_id)
        if task_instance is None or task_instance.state not in [
            State.RUNNING,
            State.NONE,
        ]:
            return ApiResponse.not_found(
                "task is not found or state is neither RUNNING nor NONE"
            )
        tis.append(task_instance)
    else:
        tis = DagRun.get_task_instances(dag_run, [State.RUNNING, State.NONE])

    logging.info("tis: " + str(tis))
    running_task_count = len(tis)

    if running_task_count > 0:
        for ti in tis:
            ti.state = State.FAILED
            ti.end_date = timezone.utcnow()
            session.merge(ti)
            session.commit()
    else:
        return ApiResponse.not_found("DagRun don't have running tasks")

    session.close()

    return ApiResponse.success({"message": f"tasks in {run_id} killed!!"})
