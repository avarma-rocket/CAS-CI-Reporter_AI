import sys
import jenkins
import requests
import os
from collections import defaultdict
from functools import lru_cache

from requests.auth import HTTPBasicAuth

class JenkinsMediator:

    """
    JenkinsMediator(url, user_login)

    Class used to interact with Jenkins, using its REST API. Provides an
    abstraction from the Jenkins API so should it ever change, interacting
    modules don't need to.

    url: str          - A string containing the URL of the Jenkins server
    user_login: tuple - A tuple containing a pair of of strings, a username and
                        a Jenkins API key.
    """

    def __init__(self, url, user_login):
        self.user_login = user_login
        self.jenkins_server = url
        username, password = user_login

        # Attempt to make a Jenkins connection, if we can't we fail fast
        try:
            self.jenkins_conn = jenkins.Jenkins(url, username, password)
        except jenkins.JenkinsException:
            print(
                "Login failed. Please check provided login details were "
                "entered correctly..."
            )
            sys.exit(1)

    """
    retrieve_test_results(self, job_list) -> list

    job_list: A list of strings denoting the names of the jobs you wish to
              retrieve results from

    output: A list of dictionaries which contain the corresponding test result
            json information for each job
    """

    def retrieve_test_results(self, job_list) -> list:
        # Build list of json test result objects for each build from each job
        job_test_results = []
        for job in job_list:
            report = self.jenkins_conn.get_build_test_report(job.name, job.nbr)
            if report is not None:
                job_test_results.append(
                    report | {"jobName": job.name.replace("%252F", "_"), "jobNumber": job.nbr, "jobNameOrig": job.name}
                )
            else:
                print(f"\033[93m~ Job {job.name} #{job.nbr} does not have test results available. Skipping!\033[0m")

        return job_test_results
    
    """
    Downloads a file from the given URL to the specified destination directory.

    Args:
        url (str): The URL of the file to download.
        dest_dir (str): The directory where the file will be saved.

    Returns:
        str: The path to the downloaded file.
    """

    def get_job_artifact_results(self, job, relative_path, dest_dir, zipped_name, session=None) -> str:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        latest_build_number = self.get_latest_job_number(job)
        username, password = self.user_login
        folder_url, short_name = self.jenkins_conn._get_job_folder(job)

        url = f"{self.jenkins_server}/{folder_url}job/{short_name}/{latest_build_number}/artifact/results/{relative_path}/{zipped_name}-failfiles/*zip*/{zipped_name}-failfiles.zip"
        filename = url.split("/")[-1] or "downloaded_file"
        dest_path = os.path.join(dest_dir, filename)

        try:
            print(f"Downloading {url}")
            # Use the passed-in session if available
            req = session if session else requests
            response = req.get(url, stream=True, verify=False, auth=HTTPBasicAuth(username, password))
            response.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded to: {dest_path}")
            return dest_path
        except requests.RequestException as e:
            print(f"Failed to download file: {e}")
            return None

    """
    get_latest_job_number(self, job_name) -> int

    job_name: str - A string storing the name of the job to query
    output: int   - An integer representing the job number
    """

    @lru_cache(maxsize=None)
    def get_latest_job_number(self, job_name) -> int:
        job_info = self.jenkins_conn.get_job_info(job_name)
        return job_info['lastBuild']['number']


    """
    get_results_matrix(self, job_list)

    job_name: str - A string storing the name of the job to query

    """
    def get_results_matrix(self, job_tests) -> dict:
        fail_count_dictionary = defaultdict(lambda: defaultdict(int))
        failing_statuses = {"FAILED", "REGRESSION"}

        for job in job_tests:
            job_name_parts = job['jobName'].split('/')
            job_type = job_name_parts[-2].split('_')[-1]
            col_key = f"{job_type}/{job_name_parts[-1]}"

            for suite in job['suites']:
                case_fail_count = 0
                row_key = None  # We'll compute this only once per suite

                for case in suite['cases']:
                    if row_key is None:
                        class_parts = case['className'].split('.')[0].split('/')
                        machine_parts = class_parts[0].split('-')
                        row_key = f"{machine_parts[1]}-{class_parts[1]}"

                    if case['status'] in failing_statuses:
                        case_fail_count += 1

                fail_count_dictionary[row_key][col_key] += case_fail_count

        # Sort only at the top level (rows)
        return dict(sorted(fail_count_dictionary.items()))
    
    """
    get_nodes_for_labels(self, fail_list)

    fail_list: list - A set of failures

    """
    def get_nodes_for_labels(self, fail_list: list):
        node_dictionary = {}
        for job_list in fail_list:
            for job in job_list:
                node_label = job.node_label
                if not node_label in node_dictionary:
                    node_info = self.jenkins_conn.get_node_info(node_label)
                    node_dictionary[node_label] = node_info['displayName']
                job.machine_name = node_dictionary[node_label]
        return