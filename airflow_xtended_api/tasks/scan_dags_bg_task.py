import logging
from multiprocessing import Process
from airflow.jobs.scheduler_job import SchedulerJob


class ScanDagsTask(Process):
    def run(self):
        scheduler_job = SchedulerJob(num_times_parse_dags=1)
        scheduler_job.heartrate = 0
        scheduler_job.run()
        try:
            scheduler_job.kill()
        except Exception:
            logging.info("Rescan Complete: Killed Job")
