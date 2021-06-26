import logging
import os
import socket

from flask import request
from airflow.api_connexion import security
from airflow.security import permissions
from airflow import settings
from airflow.www.app import csrf
from airflow.models import DagModel

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse

_hostname = socket.gethostname()


@blueprint.route("/deploy_dag", methods=["POST"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_CREATE, permissions.RESOURCE_DAG)])
def deploy_dag():
    """Custom Function for the deploy_dag API
    Upload dag file，and refresh dag to session

    args:
        dag_file: the python file that defines the dag
        force: whether to force replace the original dag file
        unpause: enable dag
        otf_syc: sync dags in foreground
    """

    logging.info("Executing custom 'deploy_dag' function")

    # check if the post request has the file part
    if "dag_file" not in request.files or request.files["dag_file"].filename == "":
        logging.warning("The dag_file argument wasn't provided")
        return ApiResponse.bad_request("dag_file should be provided")
    dag_file = request.files["dag_file"]

    force = request.form.get("force") is not None
    logging.info("deploy_dag force upload: " + str(force))

    unpause = request.form.get("unpause") is not None
    logging.info("deploy_dag in unpause state: " + str(unpause))

    otf_sync = request.form.get("otf_sync") is not None
    logging.info("create_dag in otf_sync state: " + str(otf_sync))

    is_valid_file = dag_utils.is_valid_dag_file(dag_file.filename)
    # make sure that the dag_file is a python script
    if dag_file and is_valid_file:
        dag_file_path = os.path.join(dag_utils.get_dag_folder(), dag_file.filename)

        # Check if the file already exists.
        if os.path.isfile(dag_file_path) and not force:
            logging.warning("File to upload already exists")
            return ApiResponse.bad_request(
                "The file '" + dag_file_path + "' already exists on host '" + _hostname
            )

        try:
            logging.info("Saving file to '" + dag_file_path + "'")
            dag_file.save(dag_file_path)
        except Exception:
            return ApiResponse.server_error(
                f"unable to write dag file at {dag_file_path}"
            )

    else:
        logging.warning(
            "deploy_dag file is neither a python file nor a zip file. It does not end with either .py, .pyc or .zip."
        )
        return ApiResponse.bad_request("dag_file is not a *.py(c) or *.zip file")

    # handle zip files
    is_zip_file = dag_utils.is_zip_file(dag_file.filename)

    if is_zip_file:
        dag_utils.scan_dags(otf_sync)
        return ApiResponse.success(
            {"message": "DAG Zip File [{}] has been uploaded".format(dag_file.filename)}
        )

    try:
        # import the DAG file that was uploaded
        # so that we can get the DAG_ID to execute the command to pause or unpause it
        dag_file = utils.create_module_from_file(dag_file_path)
    except Exception:
        logging.exception("Failed to get dag_file")
        return ApiResponse.server_error("Failed to get dag_file")

    try:
        if dag_file is None or dag_file.dag is None:
            logging.warning("Failed to get dag")
            return ApiResponse.server_error(
                f"No dag found in the uploaded file [{dag_file_path}]"
            )
    except Exception:
        logging.exception(f"Failed to get DAG from DAG File [{dag_file}]")
        return ApiResponse.server_error(f"Failed to get DAG from DAG File [{dag_file}]")

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

    return ApiResponse.success({"message": f"DAG File [{dag_file}] has been uploaded"})


@csrf.exempt
@blueprint.route("/deploy_dag", methods=["GET"])
def download_and_deploy_dag():
    """Custom Function for the deploy_dag API
    Upload dag file，and refresh dag to session

    args:
        dag_file_url: url to fetch the dag file
        filename: name of the fetched dag file
        force: whether to force replace the original dag file
        unpause: enable dag
        otf_syc: sync dags in foreground
    """

    logging.info("Executing custom 'download_and_deploy_dag' function")

    dag_file_url = request.args.get("dag_file_url", None)
    if dag_file_url is None or dag_file_url == "":
        logging.warning(f"dag_file_url argument wasn't provided: {dag_file_url}")
        return ApiResponse.bad_request("dag_file_url should be provided")

    filename = request.args.get("filename", None)
    if not dag_utils.is_valid_dag_file(filename):
        filename = None

    force = request.args.get("force", None) is not None
    logging.info("deploy_dag force upload: " + str(force))

    unpause = request.args.get("unpause", None) is not None
    logging.info("deploy_dag in unpause state: " + str(unpause))

    otf_sync = request.args.get("otf_sync", None) is not None
    logging.info("create_dag in otf_sync state: " + str(otf_sync))

    try:
        dag_file_path = utils.download_file(
            dag_file_url, dag_utils.get_dag_folder(), filename, force
        )
    except Exception as e:
        logging.exception(f"unable to download file from {dag_file_url}")
        if hasattr(e, "message"):
            return ApiResponse.other_error(e.message)
        return ApiResponse.bad_request(f"unable to retrive file from {dag_file_url}")

    # handle zip files
    is_zip_file = dag_utils.is_zip_file(dag_file_path)

    if is_zip_file:
        dag_utils.scan_dags(otf_sync)

        return ApiResponse.success(
            {"message": f"DAG Zip File [{dag_file_path}] has been uploaded"}
        )

    try:
        # import the DAG file that was uploaded
        # so that we can get the DAG_ID to execute the command to pause or unpause it
        dag_file = utils.create_module_from_file(dag_file_path)
    except Exception:
        logging.exception("Failed to get dag_file")
        return ApiResponse.server_error("Failed to get dag_file")

    try:
        if dag_file is None or dag_file.dag is None:
            logging.exception("Failed to get dag")
            return ApiResponse.server_error(f"DAG File [{dag_file}] has been uploaded")
    except Exception:
        logging.exception("Failed to get dag from dag_file")
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

    return ApiResponse.success({"message": f"DAG File [{dag_file}] has been uploaded"})
