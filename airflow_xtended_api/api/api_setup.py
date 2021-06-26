import time
import logging

from flask import request, g

from airflow_xtended_api.api.app import blueprint


@blueprint.before_request
def perf():
    g.tic = time.perf_counter()
    g.toc = lambda: f"{time.perf_counter() - g.tic:0.4f}"


@blueprint.after_request
def after_request_callback(response):
    logging.info(f" {request.endpoint} completed in {g.toc()} seconds")
    return response


# Alas
# import endpoints
from airflow_xtended_api.api.endpoints import *

# import error handlers
from airflow_xtended_api.api import error_handlers
