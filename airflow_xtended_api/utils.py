import logging
import os
import sys
import time
import shutil

import requests
import airflow
from airflow import configuration
from airflow import settings
from airflow.models import DagBag
from flask import Response, current_app

import airflow_xtended_api.config as config
from airflow_xtended_api.exceptions import (
    OSFileHandlingError,
    NetworkRequestFailedError,
)


def get_config_xtended_api_disabled():
    return configuration.conf.getboolean("xtended_api", "disabled", fallback=False)


def get_webserver_base_url():
    return configuration.conf.get("webserver", "BASE_URL")


def get_api_endpoint():
    return config.API_BASE_URL


def get_airflow_version():
    return airflow.__version__


def get_plugin_version():
    return config.PLUGIN_VERSION


def load_module_from_file(module_name, module_path):
    """Loads a python module from the path of the corresponding file.
    Args:
        module_name (str): namespace where the python module will be loaded,
            e.g. 'foo.bar'
        module_path (str): path of the python file containing the module
    Returns:
        A valid module object
    Raises:
        ImportError: when the module can't be loaded
        FileNotFoundError: when module_path doesn't exist
    """
    if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    elif sys.version_info[0] == 3 and sys.version_info[1] < 5:
        import importlib.machinery

        loader = importlib.machinery.SourceFileLoader(module_name, module_path)
        module = loader.load_module()
        sys.modules[module_name] = module
    elif sys.version_info[0] == 2:
        import imp

        module = imp.load_source(module_name, module_path)
        sys.modules[module_name] = module

    return module


def create_module_from_file(module_file_path):
    import hashlib

    org_mod_name, _ = os.path.splitext(os.path.split(module_file_path)[-1])
    path_hash = hashlib.sha1(module_file_path.encode("utf-8")).hexdigest()
    mod_name = f"magical_prefix_{path_hash}_{org_mod_name}"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    module = load_module_from_file(mod_name, module_file_path)
    return module


def create_module_from_string(module_name, source_text):
    import importlib.util as imp

    module_name = module_name.split(".")[0]
    mod_name = f"magical_prefix_{module_name}"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    spec = imp.spec_from_loader(mod_name, loader=None)
    module = imp.module_from_spec(spec)
    try:
        exec(source_text, module.__dict__)
        sys.modules[spec.name] = module
    except Exception as e:
        logging.warning(e)
        logging.info("Invalid Source Code")
    return module


def download_file(url, download_dir, filename=None, force=False):
    BUFFER_LENGTH = 5 * 1024 * 1024
    if not filename:
        file_path = os.path.join(download_dir, url.split("/")[-1])
    else:
        file_path = os.path.join(download_dir, filename)

    if os.path.isfile(file_path) and not force:
        raise OSFileHandlingError(f"{file_path} already exists!!")

    try:
        with requests.get(url, stream=True) as r:
            r.raw.decode_content = True
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f, length=BUFFER_LENGTH)
        return file_path
    except OSError:
        logging.exception(f"unable to write file {file_path}")
        raise OSFileHandlingError(f"unable to write file {file_path}")
    except Exception:
        logging.exception(f"unable to download file {file_path} from {url}")
        raise NetworkRequestFailedError(f"unable to download file {file_path}")
