---
mainfont: sans-serif
monofont: Victor Mono, Cascadia Code, Consolas
title: "Jenkins Reporter"
subtitle: "Design and Implementation"
toc-title: "Table of Contents"
---
## Outline
Jenkins Reporter follows these steps to produce the report:

1. First, a connection is established with the CAS Jenkins controller
2. Using the Jenkins API, a set of results for each job is returned in the form
of JSON
3. These JSON responses are parsed, and `TestFailure` objects are constructed for
each test failure
4. The collection of `TestFailure` objects are iterated over, and written to either an
Excel Spreadsheet or a Wiki Page format.


## Modules
Here is a summary of the modules which makes up Jenkins Reporter:

* **`jenkins_reporter.py`** - The top level module which orchestrates the steps
described in the [outline](#outline) above
* **`configuration.py`** - A module containing the `Configuration` class, which
represents the set of jobs to be executed
* **`jenkins_mediator.py`** - Interfaces with Jenkins through the API, 
retrieving the test result data, as well as acting as a go-between for the 
`jenkins_reporter` module and the third party `python-jenkins` module. Fulfills
Step 1 & 2 of the [outline](#outline)
* **`job_test_result_parser.py`** - Parses the results out of the JSON responses
returned through Jenkins, and returns a collection of `TestFailure` objects.
* **`test_failure.py`** - A module containing the `TestFailure` 
[dataclass](https://docs.python.org/3/library/dataclasses.html), a plain old
data (POD) object which stores information about each test failure.
* **`excel_sheet_writer.py`** - A module containing the `ExcelResultsWrapper`
class which transforms `TestFailure` objects into styled Excel tables which are
written to file.
* **`markdown_writer.py`** - A module containing the `MarkdownResultsWrapper`
class which transforms `TestFailure` objects into styled wiki tables which are
written to a markdown file.

### Dependency Graph
~~~mermaid
flowchart TD
    A["jenkins_reporter"] --> B["configuration"]
    A["jenkins_reporter"] --> C["jenkins_mediator"]
    C["jenkins_mediator"] --> G["python-jenkins"]
    A["jenkins_reporter"] --> D["job_test_result_parser"]
    D["job_test_result_parser"] --> H["test_failure"]
    A["jenkins_reporter"] --> E["excel_sheet_writer"]
    E["excel_sheet_writer"] --> I["openpyxl"]
    A["jenkins_reporter"] --> F["markdown_writer"]
    F["markdown_writer"] --> J["mdutils"]
~~~

### Module Documentation
For documentation about the functions and classes that make up Jenkins 
Reporter, consult the Pydoc [documentation](src.html).



