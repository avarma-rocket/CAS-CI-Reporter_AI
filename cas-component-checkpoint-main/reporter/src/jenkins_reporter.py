import glob
from pathlib import Path
import argparse
import shutil
import sys
from datetime import datetime
import os
import ctypes
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor

from configuration import Configuration
from jenkins_mediator import JenkinsMediator
from job_test_result_parser import JobTestResultParser
from excel_sheet_writer import ExcelResultsWrapper
from markdown_writer import MarkdownResultsWrapper
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Shared session with larger pool
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries=Retry(total=3, backoff_factor=0.5)
)
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(3, None, size)
    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(3, nameBuffer, size)
    return nameBuffer.value

if __name__ == "__main__":
    # -------------------- Check Python Version ----------------------- #
    if sys.version_info < (3,13,3):
        print(f"\033[93m~ Python version is below reccomended. Upgrade to 3.13.7 to ensure this tool functions correctly\033[0m")
        
    # -------------------- Argument Parser Definition ----------------------- #
    cmdline_arg_parser = argparse.ArgumentParser()
    credentials = cmdline_arg_parser.add_argument_group(title="Credentials")
    display_type =cmdline_arg_parser.add_argument_group(title="Display Type")
    results_download =cmdline_arg_parser.add_argument_group(title="Results Download")
    download_threads =cmdline_arg_parser.add_argument_group(title="Thread Count to Download failure files")
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
        choices=['CONF','FULL','WEEKEND','PAC','IPIC','PRIVATE']
    )
    cmdline_arg_parser.add_argument(
        "--download-threads",
        type=int,
        default=1,  # Optional: default if not provided
        help="Number of threads to use when downloading results"
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
    JENKINS_SERVER = "https://nwb-casci.dev.rocketsoftware.com"

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
            if response.lower() == "n":
                print("Skipping results download...")
                cmdline_args.results_download = None
            else:
                shutil.rmtree(results_root_local)
                os.makedirs(results_root_local)
        else:
            os.makedirs(results_root_local)

    report_file_name = "CI_Status_Results_" + job_set + "_" + date_display
    report_file_path = os.path.join(results_root_local, report_file_name)
    file_name = "CI_Status_Results_" + job_set + "_" + date_display
    if (report_display_type == "EXCEL"):
        print("Writing test results to Excel spreadsheet...")
        results_workbook = ExcelResultsWrapper(f"{report_file_path}.xlsx")
        results_workbook.build_excel_report(test_failures)
    elif(report_display_type == "WIKI"):
        print("Writing test results to Wiki spreadsheet...")
        title = date_display + " " + job_set + " (" + get_display_name() + ")"
        results_workbook = MarkdownResultsWrapper(f"{report_file_path}.md", title)
        results_workbook.build_results_matrix(results_matrix)
        results_workbook.create_quick_summary_section()
        results_workbook.build_markdown_report(test_failures)
        results_workbook.create_markdown_report()

    if cmdline_args.results_download is not None:
        print("Downloading results files")

        # --- Flatten job list and prepare download tasks ---
        download_tasks = []
        for joblist in test_failures:
            for job in joblist:
                os_type = job.os_target.split('-')[0]
                bit_type = "64" if job.os_target.split('-')[1] == "x64" else "32"
                machine_name = job.machine_name.replace("/", "_")
                relative_path = f"{os_type}/{bit_type}/{job.test_suite}"
                output_path = f"{results_root_local}/{job.job_name.replace('/', '_').replace("%252F", "_")}/{machine_name}"
                download_tasks.append((job.job_name, relative_path, output_path, job.test_suite))

        # --- Run downloads in parallel ---
        def download_result(args):
            job_name, relative_path, output_path, test_suite = args
            jenkins_connection.get_job_artifact_results(job_name, relative_path, output_path, test_suite, session=session)

        max_threads = min(cmdline_args.download_threads, max(len(download_tasks), 1))
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(download_result, download_tasks)

        # --- Optional unzip ---
        if cmdline_args.unzip_results:
            extract_to = os.path.splitext(results_root_local)[0]
            # Extract contents
            with zipfile.ZipFile(results_root_local, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f'Extracted to: {extract_to}')