from test_failure import TestFailure


def strip_config_from_url(className, jobName):
    node = className.split('.')[0]
    node_parts = node.split('/')
    os = node_parts[0].split('-')[1]
    bitism = node_parts[1]
    job_type = jobName.split('/')[-2].split('_')[-1]
    branch_name = job_type + '/' + jobName.split('/')[-1]
    os_target = os + '-' + bitism
    
    return (node, branch_name, os_target, bitism)

class JobTestResultParser:
    """
    JobTestResultParser(job_test_results)

    Class to parse job test results in json format received from a Jenkins 
    master instance. Provides methods for scanning test results for failures, 
    and collating results into POD objects for later processing.

    job_test_results: list - A list containing dictionary structures mirroring 
                             test result json files retrieved for each job from
                             the Jenkins server
    """

    def __init__(self, job_test_results):
        self.job_test_results = job_test_results

    def collate_test_failures(self) -> list:

        # Gather the failures for each job
        job_set_failures = [
            self.scan_job_for_failures(job)
            for job in self.job_test_results
        ]

        # Merge bitisms into one list for each job
        for i, next_i in zip(job_set_failures, job_set_failures[1:]):
            # If i or next_i is empty or None, skip to the next comparison.
            if not i or not next_i:
                continue

            # If branches match in different jobs, they are different bitisms
            # and should be in the same data set.
            if i[0].branch == next_i[0].branch:
                job_set_failures.append(i + next_i)
                job_set_failures.remove(i)
                job_set_failures.remove(next_i)
   
        return job_set_failures

    def scan_job_for_failures(self, job) -> list:
        if job is None:
            return []

        job_configurations = job['suites']
        # Only investigate configurations that had failing tests
        config_failures = [
            self.scan_configuration_for_failures(case, job)
            for suite in job_configurations
            for case in suite['cases']
            if case['status'] in ["FAILED", "REGRESSION"]
        ]

        # Flatten results from each configuration into one list for the whole
        # job
        job_failures = [
            test_failure
            for config in config_failures
            for test_failure in config
        ]

        return job_failures

    def scan_configuration_for_failures(self, config, job) -> list:
        # Identify configuration name so we can tag any failures with the
        # name for future reference
        className = config['className']
        config_string = strip_config_from_url(config['className'], job['jobName'])

        failed_tests = []

        test_failure = TestFailure(
            config_string[0],
            config_string[1],
            config['className'].split('.')[1],
            config['name'],
            config_string[2],
            config['age'],
            job['jobNameOrig'],
            job['jobNumber'],
            config_string[0].split("/")[0] + '/'+ config_string[3],
        )

        failed_tests.append(test_failure)

        return failed_tests
