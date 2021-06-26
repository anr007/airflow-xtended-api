from flask import Blueprint
from airflow.plugins_manager import AirflowPlugin

import airflow_xtended_api.utils as utils
from airflow_xtended_api.api import app
import airflow_xtended_api.config as config
import airflow_xtended_api.ui.app_builder_view as view


# Creating Blueprint
api_ui_blueprint = Blueprint(
    "api_ui_blueprint",
    __name__,
    template_folder="ui/templates",
    static_folder="ui/static",
    static_url_path="/static/" + view.get_route_base(),
)

api_blueprint = app.blueprint

api_view = {
    "category": config.AIRFLOW_UI_MENU_ENTRY,
    "name": config.AIRFLOW_UI_SUB_MENU_ENTRY,
    "view": view.XtendedApiView(),
}


class XtendedApi(AirflowPlugin):
    name = config.PLUGIN_NAME
    operators = []
    hooks = []
    executors = []
    menu_links = []

    if utils.get_config_xtended_api_disabled():
        flask_blueprints = []
        appbuilder_views = []
    else:
        flask_blueprints = [api_ui_blueprint, api_blueprint]
        appbuilder_views = [api_view]
