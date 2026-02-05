from pathlib import Path
from dataclasses import dataclass
from jenkins_mediator import JenkinsMediator

@dataclass
class JobConfig:
    name: str
    nbr: int

class Configuration:

    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.config_map = {
            "CONF": "jobs_conf.cfg",
            "FULL": "jobs_full.cfg",
            "WEEKEND": "jobs_weekend.cfg",
            "PAC": "jobs_PAC.cfg",
            "IPIC": "jobs_ipic.cfg",
            "PRIVATE": "jobs_private.cfg"
        }
        self.set_job_config = self.config_map["FULL"]

    def apply_config(self, job_config):
        # If job_config is not an allowed value, use default config
        # the Configuration object is initialised with, i.e. FULL
        if job_config in self.config_map.keys():
            self.set_job_config = self.config_map[job_config.upper()]

    def get_jobs_to_complete(self, jenkins_connection: JenkinsMediator) -> list:
        project_root = Path(__file__).parent.parent
        config_path = project_root.joinpath(
            self.config_dir,
            self.set_job_config
        )

        jobs_to_scan = []

        with open(config_path, 'r') as f:
            for line in f:
                job_line = line.rstrip('\n')
                job_line_parts = job_line.split(' ')

                job_name = job_line_parts[0]
                job_nbr = int(job_line_parts[1]) if len(job_line_parts) == 2 else jenkins_connection.get_latest_job_number(job_name)
                
                jobs_to_scan.append(JobConfig(job_name, job_nbr))

        return jobs_to_scan

