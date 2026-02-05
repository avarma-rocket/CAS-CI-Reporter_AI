import os
from mdutils.mdutils import MdUtils
from mdutils import Html
import re

class MarkdownResultsWrapper:
    # Reports directory path (inside full_reporter/reports)
    REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "reports")

    """
    MarkdownResultsWrapper(file_name)


    TODO: MORE INFO!!!
    """

    def __init__(self,  file_name_param: str, title: str):
        # Ensure reports directory exists
        os.makedirs(self.REPORTS_DIR, exist_ok=True)
        # Create full path for the file in reports directory
        full_path = os.path.join(self.REPORTS_DIR, os.path.basename(file_name_param))
        self.mdfile = MdUtils(file_name=full_path) 
        self.file_name = full_path

        self.mdfile.new_line("==" + title + "==\n")
        self.branches = {}

    def branch_sort_key(self,branch):
        # Extract numeric part if it exists; otherwise, handle non-numeric branches like 'trunk'
        match = re.search(r'(\d+)', branch)
        if match:
            return ('non-trunk', int(match.group()))  # Sort by the integer part if found
        else:
            return ('trunk', float('inf'))  # Keep 'trunk' at the top
    
    def build_results_matrix(self, results_matrix: dict):
        markdown_str = "===Results Matrix===\n"

        #Begin table
        markdown_str += "{| class='wikitable'\n"
        markdown_str += "|-\n"
        # Extract all unique keys from all inner dictionaries
        all_keys = set()
        for sub_dict in results_matrix.values():
            all_keys.update(sub_dict.keys())  # Collect unique keys

        print(all)
        #Create the first row
        self.branches = sorted(all_keys, key=self.branch_sort_key, reverse=True)
        markdown_str += "!Platform/Version\n"
        for branch in self.branches:
            markdown_str += "!" + branch + "\n"
        markdown_str += "!Total\n"
        markdown_str += "|-\n"

        #Create the rows with data
        for platform in results_matrix:
            markdown_str += "!" + platform + "\n"
            total_platform_fails = 0
            for branch in self.branches:
                fail_count = results_matrix.get(platform, {}).get(branch, 999999)
                if fail_count == 999999:
                    markdown_str += "|~\n"
                    fail_count = 0
                elif fail_count == 0:
                    markdown_str += "|P\n"
                else:
                    markdown_str += "!" + str(fail_count) + "\n"
                total_platform_fails += fail_count
            if total_platform_fails == 0:
                markdown_str += "|P\n"
            else:
                markdown_str += "!" + str(total_platform_fails) + "\n"
            markdown_str += "|-\n"

        #Create final row
        markdown_str += "!Total\n"
        total_fails = 0
        for branch in self.branches:
            total_branch_fails = 0
            for platform in results_matrix:
                total_branch_fails += results_matrix.get(platform, {}).get(branch, 0)
            
            if total_branch_fails == 0:
                markdown_str += "|P\n"
            else:
                markdown_str += "!" + str(total_branch_fails) + "\n"
            total_fails += total_branch_fails
        if total_fails == 0:
            markdown_str += "|P\n"
        else:
            markdown_str += "!" + str(total_fails) + "\n"
        markdown_str += "|-\n"

        #End table
        markdown_str += "|}\n"
        self.mdfile.write(markdown_str)

    def convert_to_dictionary(self, results: list) -> list:

        results_dict = []
        for branch_results in results:
            if branch_results:
                results_dict += [fail_result.to_dict() for fail_result in branch_results]
        return results_dict

    def combine_branch_fails(self, results_dict: list, branch: str) -> list:
        combined_branch_results = []
        for branch_results in results_dict:

            #In case there are other TRN machines, they get displayed in the first category
            if "Tranclass" in branch:
                if branch in branch_results['Branch']:
                    combined_branch_results.append(branch_results)
            else:
                if branch in branch_results['Branch'] and not "Tranclass" in branch_results['Branch']:
                    combined_branch_results.append(branch_results)

        return combined_branch_results
    
    def parse_os_platform(self, os: str) -> str:
        os_parts = os.split('/')
        os_name = os_parts[0].split('-')[0]
        bitism = os_parts[1]
        return os_name + '/' + bitism
    
    def parse_machine_name(self, machine: str, os: str) -> str:
        return machine + '/' + os.split('/')[1]
    
    def check_multiple_os(self, test: str, os: str, age: int, machine: str,  branch_results: list) -> tuple:
        platforms = [os]
        ages = [age]
        machines = [machine]
        if branch_results:
            to_pop = []
            for index_result, result in enumerate(branch_results):
                if test == result['Test']:
                    platforms.append(result['OS'])
                    ages.append(result['Age'])
                    machines.append(result['MachineName'])
                    to_pop.append(index_result)

            for remove_entry in sorted(to_pop, reverse=True):
                del branch_results[remove_entry] 

        return sorted(set(platforms)), max(ages), branch_results, machines

    def build_branch_report(self, branch_results: list, branch: str):

        markdown_str = ""
        if not branch_results:
            return markdown_str
        
        while branch_results:
            result = branch_results.pop(0)
            test = result['Test']

            #We combine multiple OS per branch to be under the same row
            platforms, age, branch_results, machines = self.check_multiple_os(test, result['OS'], result['Age'], result['MachineName'], branch_results)

            markdown_str += "|" + test + "\n"
            markdown_str += "|" + branch + "\n"
            markdown_str += "|"
            for platform in platforms:
                markdown_str += platform + "\n\n"
            markdown_str += "|" + str(age) + "\n"
            markdown_str += "|"
            for machine in machines:
                markdown_str += machine + "\n\n"

            for i in range(3):
                markdown_str += "|\n"
            markdown_str += "|-\n"

        return markdown_str


    def build_markdown_report(self, results: list):

        if not results:
            markdown_str = "Everything passed!!!"
            self.mdfile.write(markdown_str)
            return
        
        markdown_str = "===Failure List===\n"
        
        #Create the beginning of the table
        markdown_str += "{| class='wikitable'\n"

        #Create the first row
        headings = ["Failures", "Versions", "Platforms", "Age", "Machines", "Description", "Issue", "Assignee"]
        for heading in headings:
            markdown_str += "!" + heading + "\n"
        markdown_str += "|-\n"

        #Create the entries of the table
        results_dict = self.convert_to_dictionary(results)
        for branch in self.branches:
            combined_branch_results = self.combine_branch_fails(results_dict, branch)
            markdown_str += self.build_branch_report(combined_branch_results, branch)

        #Create the end of the table
        markdown_str += "|}"
        self.mdfile.write(markdown_str)

    def create_markdown_report(self):
        self.mdfile.create_md_file()

    def create_quick_summary_section(self):
        markdown_str = "'''''Quick Summary:'''''\n"
        markdown_str += "PLEASE MODIFY THIS WITH THE REQUIRED HIGHLIGHTS\n"
        self.mdfile.write(markdown_str)