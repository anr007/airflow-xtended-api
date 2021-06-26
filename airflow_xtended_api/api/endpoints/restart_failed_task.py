import logging

from flask import request
from airflow import settings
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.utils.state import State
from airflow.www.app import csrf
from airflow.models import DagRun, DAG

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/restart_failed_task", methods=["GET"])
@csrf.exempt
@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
    ]
)
def restart_failed_task():
    """Restart the failed task in the specified dag run.
    According to dag_id, run_id get dag_run from session,
    query task_instances that status is FAILED in dag_run,
    restart them and clear status of all task_instance's downstream of them.

    args:
        dag_id: dag id
        run_id: the run id of dag run
    """

    logging.info("Executing custom 'restart_failed_task' function")

    dag_id = request.args.get("dag_id", None)
    if dag_id is None:
        return ApiResponse.bad_request("DAG id is required")
    run_id = request.args.get("run_id", None)
    if run_id is None:
        return ApiResponse.bad_request("Run id is required")

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

    if dag is None:
        return ApiResponse.not_found("dag is not found")

    tis = DagRun.get_task_instances(dag_run, State.FAILED)
    logging.info("task_instances: " + str(tis))

    failed_task_count = len(tis)
    if failed_task_count > 0:
        for ti in tis:
            dag = DAG.partial_subset(
                self=dag,
                task_ids_or_regex=r"^{0}$".format(ti.task_id),
                include_downstream=True,
                include_upstream=False,
            )

            count = DAG.clear(
                self=dag,
                start_date=dag_run.execution_date,
                end_date=dag_run.execution_date,
            )
            logging.info("count：" + str(count))
    else:
        return ApiResponse.not_found(f"{run_id} does not have failed tasks")

    session.close()

    return ApiResponse.success(
        {"message": {"failed_task_count": failed_task_count, "clear_task_count": count}}
    )
