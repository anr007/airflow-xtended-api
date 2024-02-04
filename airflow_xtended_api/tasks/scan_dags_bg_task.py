import logging
from multiprocessing import Process
from airflow.jobs.scheduler_job_runner import SchedulerJobRunner
from airflow.jobs.job import Job, run_job


class ScanDagsTask(Process):
    def run(self):
        try:
            scheduler_job = SchedulerJobRunner(job=Job(), num_times_parse_dags=1)
            scheduler_job.heartrate = 0
            run_job(job=scheduler_job.job, execute_callable=scheduler_job._execute)
            scheduler_job.kill()
        except Exception:
            logging.info("Rescan Complete: Killed Job")
