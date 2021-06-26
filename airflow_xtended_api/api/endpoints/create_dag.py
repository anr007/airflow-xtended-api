import logging

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow import settings
from airflow.www.app import csrf
from airflow.models import DagModel

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.exceptions import DagAlreadyExistsError
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/create_dag", methods=["POST"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_CREATE, permissions.RESOURCE_DAG)])
def create_dag():
    """Custom Function for the create_dag API
    Create a dag file from the provided source，and refresh dag to session

    args:
        filename: name of the created dag file
        source_text: python source of the dag
        force: whether to force replace the original dag file
        unpause: enable dag
        otf_syc: sync dags in foreground
    """

    logging.info("Executing custom 'create_dag' function")

    file_name = request.form.get("filename")
    if file_name is None:
        return ApiResponse.bad_request("file_name is required")

    source_text = request.form.get("dag_code")
    if source_text is None:
        return ApiResponse.bad_request("dag_code is required")

    force = request.form.get("force") is not None
    logging.info("create_dag in force: " + str(force))

    unpause = request.form.get("unpause") is not None
    logging.info("create_dag in unpause state: " + str(unpause))

    otf_sync = request.form.get("otf_sync") is not None
    logging.info("create_dag in otf_sync state: " + str(otf_sync))

    try:
        dag_file = dag_utils.create_dag_file_from_source_string(
            file_name, source_text, force
        )
    except DagAlreadyExistsError as e:
        return ApiResponse.bad_request(e.message)
    except Exception as e:
        warning = "Failed to get dag_file"
        logging.warning(warning)
        logging.warning(e)
        return ApiResponse.server_error("Failed to get dag_file")

    try:
        if dag_file is None or dag_file.dag is None:
            warning = "Failed to get dag"
            logging.warning(warning)
            return ApiResponse.server_error(f"DAG File [{dag_file}] has been uploaded")
    except Exception:
        warning = "Failed to get dag from dag_file"
        logging.warning(warning)
        return ApiResponse.server_error(f"Failed to get dag from DAG File [{dag_file}]")

    dag_id = dag_file.dag.dag_id
    logging.info("dag_id: " + dag_id)

    # Refresh dag into session
    dagbag = dag_utils.get_dagbag()
    dag = dagbag.get_dag(dag_id)
    session = settings.Session()
    dag.sync_to_db(session=session)
    dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
    logging.info("dag_model:" + str(dag_model))

    dag_model.set_is_paused(is_paused=not unpause)

    dag_utils.scan_dags(otf_sync)

    return ApiResponse.success({"message": f"DAG File [{dag_file}] has been created"})
