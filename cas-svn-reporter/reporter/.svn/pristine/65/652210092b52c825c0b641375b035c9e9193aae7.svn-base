---
mainfont: sans-serif
monofont: Victor Mono, Cascadia Code, Consolas
title: "Jenkins Reporter"
subtitle: "README & Documentation"
toc-title: "Table of Contents"
---
## Outline
Jenkins Reporter is a tool which collates test results from the CAS team into
a spreadsheet, so that it can be easily interpreted by other team members.
Previously, a team member would have needed to create the spreadsheet manually,
entering the data from the Jenkins test results by hand.

## Installation
### Python
To begin using the Jenkins Reporter tool, you will need Python installed. Try
running the following at the command line:
```txt
> python --version
> python3 --version
```
If neither of these commands return a valid Python version, you will need to 
install it. 

#### Windows
For Windows, run the following command:
```txt
> winget install python
```
#### Linux 
On Linux, install the latest Python package using your package manager. Given
the Linux distributions used at AMC, one of the following will work:
```txt
> sudo apt install python # Ubuntu
> sudo dnf install python # Rocky Linux
> sudo rpm install python # Red Hat 
```

### Module Dependencies 
Jenkins Reporter makes use of the following third party modules:

* [`python-jenkins`](https://python-jenkins.readthedocs.io/en/latest/) - A 
python module for interacting with the Jenkins API
* [`openpyxl`](https://openpyxl.readthedocs.io/en/stable/) - A python module 
for reading/writing Excel spreadsheets
* [`mdutils`](https://mdutils.readthedocs.io/en/stable/) - A python module 
for reading/writing wiki-style markdown.

These third party modules, and their dependencies, are tracked in the
`requirements.txt` file at the root level of the repository.

### Virtual Environment
We'll want to install our dependencies into a Python Virtual Environment. This 
prevents the modules being installed at a system level, which could cause 
issues if you've written or make use of any other Python programs which require 
a different version of a given dependency. Refer to the Python venv 
[documentation](https://docs.python.org/3/library/venv.html) for more information.

### Installation Helper Script
At the root level of the repository, you will find the `setup.cmd` script. This
essentially performs the dependency installation steps described in the next section.

### Manual Virtual Environment installation
To create the virtual environment, run the following:
```txt
> python -m venv venv
```

This will create a folder called `venv` in the current directory containing a 
local Python installation which we will use for the Jenkins Reporter.

Once our virtual environment is created, we need to activate it. Navigate to
the `venv\Scripts\` directory and run either:

* `activate.bat` if you're using Command Prompt
* `Activate.ps1` if you're using Powershell

This places both the `venv` Python interpreter and Pip package manager at the 
front of the `$PATH`, as can be seen with the following commands:
```txt
> where.exe python
C:\<path-to-jenkins-reporter>\venv\Scripts\python.exe
C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe
C:\Users\<user>\AppData\Local\Microsoft\WindowsApps\python.exe
```
```txt
> where.exe pip
C:\<path-to-jenkins-reporter>\venv\Scripts\pip.exe
C:\Users\jholt2\AppData\Local\Programs\Python\Python312\Scripts\pip.exe
```

Finally, we can run the following `pip` command at the root level of the 
repository to install the module dependencies:
```txt
> pip install -r requirements.txt
```

## Defining Configurations
In order for us to retrieve each job's test failures, we must first define which 
jobs we wish to interrogate. We call this set of jobs a ***Configuration***.

A Configuration is simply a plaintext list of job names, which is placed in the
`config` directory at the root level of of the repository. 

> Note: The Jenkins Reporter could be expanded so a user could provide a path
to a configuration or configuration directory of their choosing. This would
involve just adding a new command line argument, and then initializing the
`Configuration` object with the provided path. **This functionality is not yet implemented!**

### Examples
An example of a configuration for the CAS FULL test runs is found below:
```txt
ED7.0_FULL_32
ED7.0_FULL_64
ED8.0_FULL_32
ED8.0_FULL_64
ED9.0_FULL_32
ED9.0_FULL_64
ED10.0_FULL_32
ED10.0_FULL_64
TRUNK_FULL_32
TRUNK_FULL_64
TRUNK_TRN_FULL_32
TRUNK_TRN_FULL_64
```

## Reporter Helper Script
At the root level of the repository, you will find the `run_reporter.cmd` script.
This will:

1. Activate the virtual environment
2. Invoke `jenkins_reporter.py`, forwarding the arguments passed in
3. Deactivate the virtual environment

You don't have to use the `run_reporter.cmd` script to run the Jenkins Reporter.
It was added as a way to simplify the execution.


## Usage
### Help
To see the Jenkins Reporter usage information, change to the `src` directory and
run the following:
```txt
> python jenkins_reporter.py --help
usage: jenkins_reporter.py [-h] [--username USERNAME] [--api-key-file API_KEY_FILE] job_set

positional arguments:
  job_set               Set of jobs you wish to gather results from e.g. CONF, FULL, WEEKEND

options:
  -h, --help            show this help message and exit

Credentials:
  --username USERNAME   Jenkins username
  --api-key-file API_KEY_FILE
                        File where Jenkins API key is stored

Display Type:
  --display-type DISPLAY_TYPE
                        Sets the display format from e.g. EXCEL, WIKI
```
> Note: You might get failures if you are running the jenkins_reporter.py outside of the 
virtual environment. To avoid that, make sure you run it ***inside*** the virtual environment,
after you set it up. Alternatively, you could type `run_reporter.cmd -h` in the root directory. More information about the script at the bottom.

### Examples
Traditional usage of this utility would see the user providing credentials, 
followed by the name of a configuration, outside of the virtual environment. 
```txt
> run_reporter.cmd --username user --api-key-file path/to/file.txt <configuration-name>
```

We can also generate a wiki style output, instead of an excel page, if we specify the `--display-type`
argument. In this case, we can simply copy the content of the output markdown to the CI wiki page.
```txt
> run_reporter.cmd --display-type WIKI --username user --api-key-file path/to/file.txt <configuration-name>
```

If credentials are not enabled on the Jenkins Controller (not recommended), then
just the configuration is required:
```txt
> run_reporter.cmd <configuration-name>
```

You can also run the scripts after you activate the virtual environment. 
In that case, we go to the `/src` folder and run `jenkins_reporter.py` with the same parameters as usual.
```txt
> python jenkins_reporter.py --username user --api-key-file path/to/file.txt <configuration-name>
```

## Internal Documentation
For more information regarding the design of the Jenkins Reporter, consult the
[documentation](docs/design.html) in the `docs` folder at the top level of the repository.
