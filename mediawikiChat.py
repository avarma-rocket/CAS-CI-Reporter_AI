import requests
from requests_ntlm import HttpNtlmAuth
import urllib3

urllib3.disable_warnings()

API = "https://nwb-devwiki.dev.rocketsoftware.com/api.php"

session = requests.Session()

# Use NTLM authentication with your Windows credentials
# Replace with your actual domain\username and password
session.auth = HttpNtlmAuth('MEDIAWIKI_DOMAIN_LOGIN', 'MEDIAWIKI_DOMAIN_PASSWORD')

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

string = ""

edit = session.post(API, data={
    "action": "edit",
    "title": "Harry_anush_CAS_CI",
    "text": string,
    "token": token,
    "format": "json"
}, verify=False)

print(edit.status_code)
