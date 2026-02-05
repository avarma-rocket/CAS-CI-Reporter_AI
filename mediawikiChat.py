import os
from dotenv import load_dotenv
import requests
from requests_ntlm import HttpNtlmAuth
import urllib3

urllib3.disable_warnings()
load_dotenv('secrets.env')


API = os.environ['MEDIAWIKI_API_URL']

session = requests.Session()

# Load environment variables from secrets.env

login = os.environ['MEDIAWIKI_DOMAIN_LOGIN'].strip().replace('\\\\', '\\')
password = os.environ['MEDIAWIKI_DOMAIN_PASSWORD'].strip()

print("Loaded login:", repr(login))
print("Loaded password length:", len(password))

# Use NTLM authentication with your Windows credentials
# Replace with your actual domain\username and password
session.auth = HttpNtlmAuth(
    login,
    password
)

# Set a proper User-Agent header (required by many MediaWiki installations)
session.headers.update({
    'User-Agent': 'MediaWikiBot/1.0 (avarma@rocketsoftware.com)'
})

# 1) Get CSRF token (skip login - auth is handled by NTLM)
r = session.get(API, params={
    "action": "query",
    "meta": "tokens",
    "format": "json"
}, verify=False)


data = r.json()
# Print status code and response

token = data['query']['tokens']['csrftoken']

# Read the combined results from the MD file
md_file_path = os.path.join(os.path.dirname(__file__), 'reports', 'CI_Combined_Results_2026_02_05.md')
with open(md_file_path, 'r', encoding='utf-8') as f:
    results_table = f.read() + "\n\n"

page_title = "Harry_anush_CAS_CI"

edit = session.post(API, data={
    "action": "edit",
    "title": page_title,
    "prependtext": results_table,
    "token": token,
    "format": "json"
}, verify=False)

print(edit.status_code)
