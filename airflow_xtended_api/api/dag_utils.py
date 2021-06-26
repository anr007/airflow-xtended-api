import logging
import os
import shutil
from pathlib import Path

from airflow import settings
from airflow.configuration import conf
from airflow.models import DagBag, DagModel
from airflow.jobs.scheduler_job import SchedulerJob

from airflow_xtended_api.config import VALID_DAG_FILE_EXT
import airflow_xtended_api.utils as utils
from airflow_xtended_api.tasks.scan_dags_bg_task import ScanDagsTask
from airflow_xtended_api.exceptions import DagAlreadyExistsError


def get_dag_folder():
    return settings.DAGS_FOLDER


def get_dagbag():
    include_examples = conf.get("core", "load_examples").lower() == "true"
    return DagBag(dag_folder=get_dag_folder(), include_examples=include_examples)


def get_all_dags():
    dags = []
    dagbag = get_dagbag()
    for dag_id in dagbag.dags:
        orm_dag = DagModel.get_current(dag_id)
        dags.append(
            {
                "dag_id": dag_id,
                "is_active": (not orm_dag.is_paused) if orm_dag is not None else False,
            }
        )
    return dags


def check_dag_exists(dag_id):
    # Check to make sure that the DAG you're referring to, already exists.
    dag_bag = get_dagbag()
    if dag_id is not None and dag_id not in dag_bag.dags:
        logging.info(
            f"DAG_ID '{str(dag_id)}' was not found in the DagBag list '{str(dag_bag.dags)}'"
        )
        return False
    return True


def create_dag_file_from_source_string(file_name, source_text, overwrite=False):
    base_dag_dir = get_dag_folder()
    dag_file = Path(base_dag_dir + os.sep + file_name)
    if dag_file.exists() and (overwrite is False):
        raise DagAlreadyExistsError(
            f"{dag_file} already exists, set force to overwrite!"
        )
    logging.info(source_text)
    logging.info(type(source_text))
    dag_file.write_text(source_text)
    return utils.create_module_from_file(str(dag_file.absolute()))


def scan_dags_job():
    scheduler_job = SchedulerJob(num_times_parse_dags=1)
    scheduler_job.heartrate = 0
    scheduler_job.run()
    try:
        scheduler_job.kill()
    except Exception:
        logging.info("Rescan Complete: Killed Job")


def scan_dags(synchronous):
    if conf.get("core", "sql_alchemy_conn").startswith("sqlite"):
        logging.info(
            "Ondemand DAG scan might not work correctly: Using sqlite backend!!"
        )
    if synchronous:
        scan_dags_job()
    else:
        # start in a different process
        process = ScanDagsTask()
        process.start()
        logging.info(f"scan_dags process id: {process.pid}")


def empty_dag_folder():
    dag_folder = get_dag_folder()
    for filename in os.listdir(dag_folder):
        filepath = os.path.join(dag_folder, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)
    logging.info("dag folder emptied!!")


def is_valid_dag_file(filename):
    return (
        filename
        and filename.strip().split(os.sep)[-1].split(".")[-1].lower()
        in VALID_DAG_FILE_EXT
    )


def is_zip_file(filename):
    return (
        filename and filename.strip().split(os.sep)[-1].split(".")[-1].lower() == "zip"
    )
