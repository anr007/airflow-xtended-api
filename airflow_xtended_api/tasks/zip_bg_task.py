import logging
import threading

from airflow_xtended_api.tasks.bg_task import BackgroundTask
from airflow_xtended_api.api.dag_utils import get_dag_folder
from airflow_xtended_api.utils import download_file


class ZipDownloadTask(BackgroundTask):
    def run(self, url):
        logging.info(get_dag_folder())
        logging.info(threading.current_thread().ident)
        try:
            download_file(url, get_dag_folder())
        except Exception:
            logging.exception("download failed")
        logging.info("completed")
