import logging

from airflow import settings
from airflow.api_connexion import security
from airflow.security import permissions
from airflow.www.app import csrf
from airflow.models import DagModel
from airflow.utils import timezone

from airflow_xtended_api.api.app import blueprint
import airflow_xtended_api.utils as utils
from airflow_xtended_api.api.response import ApiResponse


@blueprint.route("/refresh_all_dags", methods=["GET"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG)])
def refresh_all_dags():
    """Custom Function for the refresh_all_dags API.
    Refresh all dags.
    """
    logging.info("Executing custom 'refresh_all_dags' function")
    try:
        session = settings.Session()
        orm_dag_list = session.query(DagModel).all()
        for orm_dag in orm_dag_list:
            if orm_dag:
                orm_dag.last_expired = timezone.utcnow()
                session.merge(orm_dag)
        session.commit()
    except Exception as e:
        error_message = (
            "An error occurred while trying to Refresh all the DAGs: " + str(e)
        )
        logging.error(error_message)
        return ApiResponse.server_error(error_message)

    return ApiResponse.success({"message": "All DAGs are now up-to-date!!"})
