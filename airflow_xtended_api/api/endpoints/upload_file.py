import logging
import os
import socket

from flask import request
from airflow import settings
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/upload_file", methods=["POST"])
@csrf.exempt
@security.requires_access([])
def upload_file():
    """Custom Function for the upload_file API.
    Upload files to the specified path.
    """
    logging.info("Executing custom 'upload_file' function")

    # check if the post request has the file part
    if (
        "file" not in request.files
        or request.files["file"] is None
        or request.files["file"].filename == ""
    ):
        logging.warning("The file argument wasn't provided")
        return ApiResponse.bad_request("file should be provided")
    file = request.files["file"]

    path = request.form.get("path")
    if path is None:
        path = dag_utils.get_dag_folder()

    force = request.form.get("force") is not None
    logging.info("deploy_dag force upload: " + str(force))

    # save file
    save_file_path = os.path.join(path, file.filename)

    # Check if the file already exists.
    if os.path.isfile(save_file_path) and not force:
        logging.warning("File to upload already exists")
        hostname = socket.gethostname()
        return ApiResponse.bad_request(
            f"The file {save_file_path} already exists on host {hostname}"
        )

    logging.info(f"Saving file to '{save_file_path}'")
    try:
        file.save(save_file_path)
    except Exception:
        logging.exception(f"Unable to save {save_file_path}")
        return ApiResponse.server_error(f"Unable to save {save_file_path}")

    return ApiResponse.success(
        {"message": "File [{}] has been uploaded".format(save_file_path)}
    )
