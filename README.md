# Automated Wiki Updater

This tool generates Jenkins CI status reports and automatically uploads them to MediaWiki.

## Prerequisites

- Python 3.x installed
- Access to CASCI and CCSERV Jenkins servers
- API tokens for both Jenkins servers

## Setup Instructions

### 1. Create API Token Files

Create two text files in the project root directory containing your Jenkins API tokens:

- **`casci_token.txt`** - Contains your CASCI Jenkins API token
- **`ccserv_token.txt`** - Contains your CCSERV Jenkins API token

> **Note:** Keep these files secure and do not commit them to version control.

### 2. Set Up Virtual Environment

Open a terminal in the project root directory and run:

```cmd
.\setup.cmd
```

### 3. Configure Environment

Create a `secrets.env` file in the project root with your MediaWiki credentials:

```env
MEDIAWIKI_API_URL=https://nwb-devwiki.dev.rocketsoftware.com/api.php
MEDIAWIKI_DOMAIN_LOGIN=Rocket Login
MEDIAWIKI_DOMAIN_PASSWORD=Rocket Password
```

Replace `Rocket Login` and `Rocket Password` with your actual credentials.

## Usage

Run the reporter using the following command:

```cmd
.\run_full_reporter.cmd <JOB_CONFIG> --username <your_username> --ccserv-key-file .\ccserv_token.txt --casci-key-file .\casci_token.txt
```

### Available Job Configurations

| Config | Description |
|--------|-------------|
| `CONF` | Configuration jobs |
| `FULL` | Full test suite |
| `IPIC` | IPIC-related jobs |
| `PAC` | PAC-related jobs |
| `PRIVATE` | Private jobs |
| `WEEKEND` | Weekend test runs |

### Example

```cmd
.\run_full_reporter.cmd PAC --username avarma --ccserv-key-file .\ccserv_token.txt --casci-key-file .\casci_token.txt
```

## Output

Reports are generated in the `reports/` directory and automatically uploaded to MediaWiki.
