import logging
import os

from airflow.www import auth
from airflow.security import permissions
from flask_appbuilder import (
    expose as app_builder_expose,
    BaseView as AppBuilderBaseView,
)

import airflow_xtended_api.utils as utils
import airflow_xtended_api.api.dag_utils as dag_utils
from airflow_xtended_api.ui.docs import api_metadata
from airflow_xtended_api.config import VIEW_BASE_URL, VIEW_BASE_ROUTE


required_permissions = [(permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE)]


def get_route_base():
    return VIEW_BASE_ROUTE


class XtendedApiView(AppBuilderBaseView):
    """API View which extends either flask AppBuilderBaseView or flask AdminBaseView"""

    route_base = VIEW_BASE_URL

    # '/' Endpoint where the Admin page is which allows you to view the APIs available and trigger them
    @app_builder_expose("/")
    @auth.has_access(required_permissions)
    def list(self):

        return self.render_template(
            "/doc_index.jinja.html",
            airflow_webserver_base_url=utils.get_webserver_base_url(),
            api_endpoint=utils.get_api_endpoint(),
            apis_metadata=api_metadata,
            airflow_version=utils.get_airflow_version(),
            plugin_version=utils.get_plugin_version(),
            static_base_route=VIEW_BASE_ROUTE,
            dags=dag_utils.get_all_dags(),
        )
