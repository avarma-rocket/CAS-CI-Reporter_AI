import sys
import jenkins


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
        job_test_results = [
            self.jenkins_conn.get_build_test_report(job.name, job.nbr) | {"jobName": job.name, "jobNumber": job.nbr}
            for job in job_list
        ]

        return job_test_results

    """
    get_latest_job_number(self, job_name) -> int

    job_name: str - A string storing the name of the job to query
    output: int   - An integer representing the job number
    """

    def get_latest_job_number(self, job_name) -> int:
        job_info = self.jenkins_conn.get_job_info(job_name)
        return job_info['lastBuild']['number']


    """
    get_results_matrix(self, job_list)

    job_name: str - A string storing the name of the job to query

    """
    def get_results_matrix(self, job_tests) -> dict:
        
        fail_count_dictionary = {}
        for job in job_tests:
            for child_report in job['childReports']:
                label = child_report['child']['url'].split('label=')[1].split('/')[0]
                print(label)
                row_key = label.split('.')[0]
                if "3RD_PARTY" in label[len(row_key)+1:]:
                    col_key = label[len(row_key)+1:].split('_', 1)[0]
                else:     
                    col_key = label[len(row_key)+1:].rsplit('_', 1)[0]
                print(col_key)
                
                if row_key in fail_count_dictionary.keys():
                    if col_key in fail_count_dictionary[row_key].keys():
                        fail_count_dictionary[row_key][col_key] += child_report['result']['failCount']
                    else:
                        fail_count_dictionary[row_key][col_key] = child_report['result']['failCount']
                else:
                    fail_count_dictionary[row_key] = {}
                    fail_count_dictionary[row_key][col_key] = child_report['result']['failCount']

            
        return {key: value for key, value in sorted(fail_count_dictionary.items())}
    
    """
    get_nodes_for_labels(self, fail_list)

    fail_list: list - A set of failures

    """
    def get_nodes_for_labels(self, fail_list: list):
        node_dictionary = {}
        for job_list in fail_list:
            for job in  job_list:
                node_label = job.node_label
                if not node_label in node_dictionary:
                    node_info = self.jenkins_conn.get_node_info(node_label)
                    node_dictionary[node_label] = node_info['description']
                job.machine_name = node_dictionary[node_label]
        return