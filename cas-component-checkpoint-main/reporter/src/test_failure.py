from dataclasses import dataclass


@dataclass
class TestFailure:

    """
    TestFailure(branch, test_suite, test_case, os_target, age)

    A plain old object (POD) record for storing information regarding test
    failures
    """
    node_label: str
    branch: str
    test_suite: str
    test_case: str
    os_target: str
    age: str
    job_name: str
    job_num: int
    machine_name: str = ''

    def __lt__(self, other):
        return (
            f"{self.test_suite}.{self.test_case}"
            < f"{other.test_suite}.{other.test_case}"
        )

    def __gt__(self, other):
        return (
            f"{self.test_suite}.{self.test_case}"
            > f"{other.test_suite}.{other.test_case}"
        )

    def to_list(self):
        return [
            self.node_label,
            self.branch,
            self.test_suite + "." + self.test_case,
            self.os_target,
            self.age,
            self.job_name,
            self.job_num,
            self.machine_name,
        ]
    def to_dict(self):
        return {
            "NodeLabel": self.node_label,
            "Branch": self.branch,
            "Test": self.test_suite + "." + self.test_case,
            "OS": self.os_target,
            "Age": self.age,
            "JobName": self.job_name,
            "JobNumber": self.job_num,
            "MachineName": self.machine_name,
        }
    
