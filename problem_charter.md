
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
We decided to hold a meeting with our stake holder as we initially had some questions about the project as we were unfamilliar with the tooling. 

This meeting also helped us gain a starting plan for the order of features we would implement

There was a clear path for undertaking the project so there wasnt much brainstorming needed. Once we had access to the reporter tool we used GitHub Copilot inside of VS Code to gain some information about it.

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

#### Prompts
We are initiating a project with our project shareholder Marta. Draft an email with the following content and ask to arrange a meeting.

Project outline: Extend the existing reporter tool so that test results are automatically published to the wiki via CI, including checking checksums to know if it is a previous failure, and suggestions from previous results. Jenkins would automatically trigger the reporter upon job completion and use stored secrets for authentication.
Value: Makes test logs and results instantly accessible; removes repetitive manual updates; improves consistency across CI runs.

Questions: 
We are initiating a project with our project shareholder Marta. Draft an email with the following content and ask to arrange a meeting.

Project outline: Extend the existing reporter tool so that test results are automatically published to the wiki via CI, including checking checksums to know if it is a previous failure, and suggestions from previous results. Jenkins would automatically trigger the reporter upon job completion and use stored secrets for authentication.
Value: Makes test logs and results instantly accessible; removes repetitive manual updates; improves consistency across CI runs.

Questions: 
1. What is the existing reporter tool and how do we get access to it.
2. Are we able to run the reporter tool with our current credentials or do we need to request new ones?
3. Would you be able to elaborate on how to implement the checksums into this project.

They already know what the project is so there doesnt need to be a full explanation only a brief reminder

Make it more casual

### Diagram
![alt text]({C363B2C7-B91C-47A0-B748-604017B35B39}.png)

### Implementation
The tool we were building from was split into two seperate projects. One takes the test results from the old Jenkins CI server and the second takes from the newer Jenkins CI server. One of the main objectives was to combine the two so that one command run would collect both test results. 

Both programs are ran but runnin the run_reporter.cmd script which sets up the virtual environment and calls the respecitve jenkins_reporter.py program. Because of this it was easy to edit one of the scripts to call both reporters one after the other. GitHub Copilot was used to assist this using the following prompts:

|Prompt (Claude Opus 4.5)|Notes|
|-|-|
|make this script run the the jenkins_reporter.py in each directory. You will need to update the arguments to allow for two different api keys and assign them to the respective script. the arguments should be ccserv-api-key and casci-api-key|This worked increadibly well for combining the two, after and initial run we did find some minor issues however. The model did not anticipate that the called python scripts take a file path and not the contents of the files so further prompting was needed|
|can the api keys be passed as files|This was only intended to ask the model about the script however it provided a solution to the problem and fixed it for us|