import glob
from pathlib import Path
import argparse
import shutil
import sys
from datetime import datetime
import os
import ctypes
import zipfile

from configuration import Configuration
from jenkins_mediator import JenkinsMediator
from job_test_result_parser import JobTestResultParser
from excel_sheet_writer import ExcelResultsWrapper
from markdown_writer import MarkdownResultsWrapper

def get_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(3, None, size)
    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(3, nameBuffer, size)
    return nameBuffer.value
    
if __name__ == "__main__":
    # -------------------- Argument Parser Definition ----------------------- #
    cmdline_arg_parser = argparse.ArgumentParser()
    credentials = cmdline_arg_parser.add_argument_group(title="Credentials")
    display_type =cmdline_arg_parser.add_argument_group(title="Display Type")
    results_download =cmdline_arg_parser.add_argument_group(title="Results Download")
    credentials.add_argument(
        "--username",
        help="Jenkins username",
        default=None
    )
    credentials.add_argument(
        "--api-key-file",
        help="File where Jenkins API key is stored",
        default=None
    )
    cmdline_arg_parser.add_argument(
        "job_set",
        help="Set of jobs you wish to gather results from e.g. CONF, FULL, WEEKEND, PAC",
        choices=['CONF','FULL','WEEKEND','PAC','IPIC']
    )
    display_type.add_argument(
        "--display-type",
        help="Sets the display format from e.g. EXCEL, WIKI",
        choices=['WIKI','EXCEL'],
        default="WIKI")
    
    results_download.add_argument(
        "--results-download",
        help="Supply flag to download results files to specified location"
    )
    results_download.add_argument(
        "--unzip-results",
        action="store_true", 
        help="If set, unzip the results in the results-download folder"
    )
     # ---------------------------- Main Script Begins ----------------------- #
    cmdline_args = cmdline_arg_parser.parse_args()

    # Read the Jenkins API key from file, if it's been provided
    api_key = ""
    if cmdline_args.api_key_file is not None:
        if cmdline_args.username is not None:
            with open(cmdline_args.api_key_file, 'r') as key_file:
                api_key = key_file.readline()
        else:
            print(
                "API key supplied without a username, "
                "please provide a username..."
            )
            sys.exit(1)
    else:
        print("Warning: No API key file provided...")

    report_display_type = cmdline_args.display_type.upper()
    job_set = cmdline_args.job_set.upper()

    job_config = Configuration("config")
    job_config.apply_config(job_set)

    LOGIN = (cmdline_args.username, api_key if len(api_key) > 0 else None)
    JENKINS_SERVER = "https://nwb-ccserv.dev.rocketsoftware.com"

    jenkins_connection = JenkinsMediator(JENKINS_SERVER, LOGIN)
    print("Successfully connected to Jenkins using provided credentials...")
    print(f"Reading jobs from the {job_set} job set...")
    jobs = job_config.get_jobs_to_complete(jenkins_connection)

    print("Gathering test results...")
    job_tests = jenkins_connection.retrieve_test_results(jobs)

    results_matrix = {}
    if (report_display_type == "WIKI"):
        print("Obtaining the results matrix...")
        results_matrix = jenkins_connection.get_results_matrix(job_tests)

    print("Parsing test results...")
    test_parser = JobTestResultParser(job_tests)
    test_failures = test_parser.collate_test_failures()

    print("Retrieving machine information...")
    jenkins_connection.get_nodes_for_labels(test_failures)

    date = datetime.now()
    date_display = date.strftime("%Y-%m-%d")

    results_root_local=""
    if cmdline_args.results_download is not None:
        results_file_name = "results_" + date_display 
        results_root_local = os.path.join(cmdline_args.results_download, results_file_name)
        if os.path.exists(results_root_local):
            response = ""
            while (response.lower() not in ["y","n"]):
                response = input("Results folder " + results_root_local + " already exists, delete? [y/n] ")
            if response.lower() == "y":
                shutil.rmtree(results_root_local)
                os.makedirs(results_root_local)
        else:
            os.makedirs(results_root_local)

    report_file_name = "OldCI_Status_Results_" + job_set + "_" + date_display 
    report_file_path = os.path.join(results_root_local, report_file_name)
    if (report_display_type == "EXCEL"):
        print("Writing test results to Excel spreadsheet...")
        results_workbook = ExcelResultsWrapper(f"{report_file_path}.xlsx")
        results_workbook.build_excel_report(test_failures)
    elif(report_display_type == "WIKI"):
        print("Writing test results to Wiki spreadsheet...")
        title = date_display  + " " + job_set + " (" + get_display_name() + ")"
        results_workbook = MarkdownResultsWrapper(f"{report_file_path}.md", title)
        results_workbook.build_results_matrix(results_matrix)
        results_workbook.create_quick_summary_section()
        results_workbook.create_machine_info_section()
        results_workbook.build_markdown_report(test_failures)
        results_workbook.create_markdown_report()

    if cmdline_args.results_download is not None:
        print("Downloading results files")
        nwb_root = "\\\\nwb-ccserv.dev.rocketsoftware.com\\"
        results_set = set()
        for joblist in test_failures:
            for job in joblist:
                file_path = nwb_root + job.machine_name + "\\Results\\" + job.job_name + "-" + str(job.job_num) + "\\Results\\"
                # Stash results directory in a map and check its existence so we don't end up downloading results twice
                if file_path in results_set:
                    continue
                results_set.add(file_path)

                output_path = os.path.join(results_root_local, job.job_name, job.machine_name)
                output_path = output_path.strip() # Remove leading/trailing whitespace and newlines.
                if not os.path.exists(output_path):
                    print("Creating output folder " + output_path)
                    os.makedirs(output_path)
                for foldername in glob.glob(os.path.join(file_path, '*-failfiles/*.zip')):
                    zip_filename = os.path.basename(foldername) 
                    testfixture_folder = os.path.basename(os.path.dirname(foldername)) 
                    testfixture_prefix = testfixture_folder.replace('-failfiles', '')
                    new_filename = f"{testfixture_prefix}_{zip_filename}"
                    folder_path = os.path.join(output_path, new_filename)
                    shutil.copy(foldername, folder_path)
                    if cmdline_args.unzip_results:
                        extract_to = os.path.splitext(folder_path)[0] 
                        # Extract contents
                        with zipfile.ZipFile(folder_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_to)
                        print(f'Extracted to: {extract_to}')
