import logging

from werkzeug.exceptions import HTTPException

from airflow_xtended_api.api.app import blueprint
from airflow_xtended_api.api.response import ApiResponse


@blueprint.app_errorhandler(Exception)
def handle_any_error(e):
    logging.exception("Unhandle exception found!!")
    if isinstance(e, HTTPException):
        return ApiResponse.error(e.code, repr(e))
    return ApiResponse.server_error(repr(e))
