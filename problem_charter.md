
# Problem Charter

## Problem
Extend the existing reporter tool so that test results are automatically published to the wiki via CI, including checking checksums to know if it is a previous failure, and suggestions from previous results. Jenkins would automatically trigger the reporter upon job completion and use stored secrets for authentication.

## Value
Makes test logs and results instantly accessible; removes repetitive manual updates; improves consistency across CI runs.

## Project Steps
1. Start with getting the reporter to run (after setup and token creation this should just download a report file) — start with Jenkins-reporter.py PAC
2. Auto upload to wiki (without merging CI tables)
3. Try and merge CI tables to one
4. Create column for error checksums

## Success Metrics
- **Reporter runs automatically in CI**: Jenkins successfully triggers the reporter script at the end of relevant jobs.
- **Report file downloads reliably**: The reporter consistently retrieves the expected report file without manual intervention.
- **Wiki auto-upload works**: CI publishes updated test results to the wiki on each run.
- **Checksum generation is accurate**: All test results include a checksum to detect repeated failures.
- **Historical suggestions appear**: When a checksum matches a previous failure, the wiki page displays suggestions or context from earlier runs.
- **Merged CI tables function correctly**: Multiple CI result tables are successfully merged into one consolidated view without data loss.
- **No manual updates required**: Stakeholders no longer need to manually update CI result logs on the wiki.
- **Access time reduced**: Stakeholders can access latest results within minutes of job completion.

## Stakeholder Communication & Brainstorming
We decided to hold a meeting with our stakeholder as we initially had some questions about the project as we were unfamilliar with the tooling. 

This meeting also helped us gain a starting plan for the order of features we would implement.

There was a clear path for undertaking the project so there wasn't much brainstorming needed. Once we had access to the reporter tool we used GitHub Copilot inside of VS Code to gain some information about it.

| Prompt | Did it help? |
|--------|--------------|
| What are the arguments in this file?  | This instantly helped with understanding the sytax of the provided script and allowed us to start testing quickly.|
|Here are two wiki tables, combine them into one coheasive table. (wikitables)| Using this prompt helped us figure out what the expected output would be for the reporter scripts |

### Drafted Email Using M365 (Not Sent)
Subject: Quick catch‑up on the reporter tool project?
Hi Marta,
Hope you're doing well! We're starting to move ahead with the reporter tool extension work — the bit where CI automatically publishes test results to the wiki and we use checksums to spot repeat failures.
We just had a couple of questions before we dive in:

1. What’s the current reporter tool we should be using, and how do we get access to it?
2. Can we run it with our existing credentials, or do we need new ones?
3. And could you share a bit more detail on how you'd like the checksum part to work?

Would you be up for a quick meeting to walk through these?
Thanks!
Harry

|Prompts|
|-|
|We are initiating a project with our project shareholder Marta. Draft an email with the following content and ask to arrange a meeting
Project outline: Extend the existing reporter tool so that test results are automatically published to the wiki via CI, including checking checksums to know if it is a previous failure, and suggestions from previous results. Jenkins would automatically trigger the reporter upon job completion and use stored secrets for authentication. Value: Makes test logs and results instantly accessible; removes repetitive manual updates; improves consistency across CI runs. We are initiating a project with our project shareholder Marta. Draft an email with the following content and ask to arrange a meeting. Project outline: Extend the existing reporter tool so that test results are automatically published to the wiki via CI, including checking checksums to know if it is a previous failure, and suggestions from previous results. Jenkins would automatically trigger the reporter upon job completion and use stored secrets for authentication. Value: Makes test logs and results instantly accessible; removes repetitive manual updates; improves consistency across CI runs.Questions: 1. What is the existing reporter tool and how do we get access to it. 2. Are we able to run the reporter tool with our current credentials or do we need to request new ones? 3. Would you be able to elaborate on how to implement the checksums into this project.|
|They already know what the project is so there doesnt need to be a full explanation only a brief reminder|
|Make it more casual|

### Diagram
![Architecture Diagram]({C363B2C7-B91C-47A0-B748-604017B35B39}.png)

### Implementation
The tool we were building from was split into two seperate projects. One takes the test results from the old Jenkins CI server and the second takes from the newer Jenkins CI server. One of the main objectives was to combine the two so that one command run would collect both test results. 

Both programs are run by running the run_reporter.cmd script which sets up the virtual environment and calls the respecitve jenkins_reporter.py program. Because of this it was easy to edit one of the scripts to call both reporters one after the other. GitHub Copilot was used to assist this using the following prompts:

|Prompt (Claude Opus 4.5)|Notes|
|-|-|
|make this script run the the jenkins_reporter.py in each directory. You will need to update the arguments to allow for two different api keys and assign them to the respective script. the arguments should be ccserv-api-key and casci-api-key|This worked increadibly well for combining the two, after and initial run we did find some minor issues however. The model did not anticipate that the called python scripts take a file path and not the contents of the files so further prompting was needed|
|can the api keys be passed as files|This was only intended to ask the model about the script however it provided a solution to the problem and fixed it for us|

Once the script was made to run both reporters we needed to combine the results into a single report. To start we wanted to move the report output location to a central folder. This again was done with the assistence of AI.

|Prompt (Claude Opus 4.5)|Notes|
|-|-|
|create a reports folder and output all reports to this directory|This did create a reports folder however it didnt change the output location of the uncombined files which was was we intended|
|make sure the original report files are generated inside the reports directory as well|This again did not change what we needed it to do, this if probably becuase both prompts we not specific enough|
|change this file to generate its report inside the report directory inside /full_reporter|As this was more specific and pointed at the file we wanted to update it was successful in changing the output location|
|do the same with this file|Although an unclear prompt this did what we expected as made the same changes to the other file we provided|

Next we needed to combine the generated files into a single report. As there were different types of report with slightly different formats it was important to have a script that would allow for the differences.

|Prompts (Claude Opus 4.5)|Notes|
|-|-|
|in the reports directory is every variation of report change combine_results.py to allow for these different types. Each report should be combined with it matching OldCI version|This did exactly what we needed it to however we noticed that some of the values werent being preserved which was a major issue|
|make sure the exact values in the uncombined files are preserved in the combined file|This updated the combine_results.py to dynamically parse the reports instead of fill a template however this still did not preserve the exact values|
|the values are still not being preserved as there are numbers in the original and only letters in the combined|After being more specific with what we needed to be preserved it was able acheive what we needed|


After combining both scripts, we generated a new script which would take the output of combine_results.py and upload the dev.wiki. The script requires a secrets.env which contains three entries: 
    - MEDIAWIKI_API_URL
    - MEDIAWIKI_DOMAIN_LOGIN
    - MEDIAWIKI_DOMAIN_PASSWORD

Where the API_URL is the URL to the dev wiki api and the login and password are the user's rocketsfotware user and password. 

We used GitHub Copilot to create the api calls and script to the wiki to edit a page. We included a link to the dev wiki documentation to provide refernece and examples for how to code.

|Prompts (Claude Opus 4.5)|Notes|
|-|-|
|Extend the existing reporter tool so that test results are automatically published to the wiki via CI, including checking checksums to know if it is a previous failure, and suggestions from previous results. Jenkins would automatically trigger the reporter upon job completion and use stored secrets for authentication. Value: Makes test logs and results instantly accessible; removes repetitive manual updates; improves consistency across CI runs.| This prompt generated a good template with parts to fillout to enter the correct url and login and password. However it had hardcoded login details inside the code.|
|Ive added MEDIAWIKI_DOMAIN_LOGIN and MEDIAWIKI_DOMAIN_PASSWORD into my secrets.env how can i reference them in my code| This prompt was concise and specifc therefore was carried out correctly. It used os python library to use env variables. However it was not parsing the username correctly because of additional backslashes not being added eg. rocketsoftware.com \\\\\\\\ avarma having 2 extra \|
|rocketsoftware.com\\\\avarma has 2 extra \ |Giving this simple prompt solved the problem quicky with minimal code changes.|
