import logging
import json

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


@blueprint.route("/run_task_instance", methods=["POST"])
@csrf.exempt
@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
    ]
)
def run_task_instance():
    """Run specified tasks, skip the rest
    According to dag_id, run_id get dag_run from session,
    Obtain the task instances that need to be run according to tasks，
    Define the status of these task instances as None,
    and define the status of other task instances that do not need to run as SUCCESS

    args:
        dag_id: dag id
        run_id: the run id of dag run
        tasks: the task id of task instance of dag, Multiple task ids are split by ','
        conf: define dynamic configuration in dag
    """

    logging.info("Executing custom 'run_task_instance' function")

    dag_id = request.form.get("dag_id")
    if dag_id is None:
        return ApiResponse.bad_request("DAG id is required")
    run_id = request.form.get("run_id")
    if run_id is None:
        return ApiResponse.bad_request("Run id is required")
    tasks = request.form.get("tasks")
    if tasks is None:
        return ApiResponse.bad_request("Tasks is required")
    conf = request.form.get("conf")

    dag_id = dag_id.strip()
    run_id = run_id.strip()
    tasks = tasks.strip()

    if not dag_utils.check_dag_exists(dag_id):
        return ApiResponse.bad_request(
            "The DAG ID '" + str(dag_id) + "' does not exist"
        )

    dagbag = dag_utils.get_dagbag()

    run_conf = None
    if conf:
        try:
            run_conf = json.loads(conf)
        except ValueError:
            return ApiResponse.error("Failed", "Invalid JSON configuration")
        except Exception:
            logging.exception("unable to handle {conf}, ignoring..")

    dr = DagRun.find(dag_id=dag_id, run_id=run_id)
    if dr:
        return ApiResponse.not_found("run_id {} already exists".format(run_id))

    logging.info("tasks: " + str(tasks))
    task_list = tasks.split(",")

    session = settings.Session()

    if dag_id not in dagbag.dags:
        return ApiResponse.not_found("Dag id {} not found".format(dag_id))

    dag = dagbag.get_dag(dag_id)
    logging.info("dag: " + str(dag))

    for task_id in task_list:
        try:
            task = dag.get_task(task_id)
        except TaskNotFound:
            return ApiResponse.not_found(
                "dag task of {} is not found".format(str(task_id))
            )
        logging.info("task：" + str(task))

    execution_date = timezone.utcnow()

    dag_run = dag.create_dagrun(
        run_id=run_id,
        execution_date=execution_date,
        state=State.RUNNING,
        conf=run_conf,
        external_trigger=True,
    )

    tis = dag_run.get_task_instances()
    for ti in tis:
        if ti.task_id in task_list:
            ti.state = None
        else:
            ti.state = State.SUCCESS
        session.merge(ti)

    session.commit()
    session.close()

    return ApiResponse.success(
        {"execution_date": (execution_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"))}
    )
