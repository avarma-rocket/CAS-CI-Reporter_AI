import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_UNDERSCORE = datetime.now().strftime("%Y_%m_%d")

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

NEW_CI_FILE = os.path.join(REPORTS_DIR, f"CI_Status_Results_{TODAY}.md")
OLD_CI_FILE = os.path.join(REPORTS_DIR, f"OldCI_Status_Results_{TODAY}.md")
COMBINED_FILE = os.path.join(REPORTS_DIR, f"CI_Combined_Results_{TODAY_UNDERSCORE}.md")

# Platform name mappings (normalize to lowercase keys)
PLATFORM_MAP = {
    'rh-x64': 'rh-x64', 'rh_64': 'rh-x64',
    'rh-x86': 'rh-x86', 'rh_32': 'rh-x86',
    'win-x64': 'win-x64', 'win_64': 'win-x64',
    'win-x86': 'win-x86', 'win_32': 'win-x86',
}

def read_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def parse_matrix_simple(content):
    """Simpler parsing approach for the matrix."""
    results = {}
    versions = []
    current_platform = None
    
    lines = content.split('\n')
    in_matrix = False
    
    for i, line in enumerate(lines):
        if "Results Matrix" in line:
            in_matrix = True
            continue
        if in_matrix and "|}" in line:
            break
        if not in_matrix:
            continue
        
        # Get versions from header
        if '!Platform/Version' in line:
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('!') and 'Platform' not in lines[j]:
                ver = lines[j].strip().lstrip('!').strip()
                if ver and ver != 'Total' and ver != '|-':
                    versions.append(ver)
                j += 1
    
    # Re-parse for data
    in_matrix = False
    for line in lines:
        if "Results Matrix" in line:
            in_matrix = True
            continue
        if in_matrix and "|}" in line:
            break
        if not in_matrix or line.strip() == '|-':
            continue
        
        if line.startswith('!') and 'Platform' not in line and 'Total' not in line:
            platform_raw = line[1:].strip().lower()
            current_platform = PLATFORM_MAP.get(platform_raw, platform_raw)
            results[current_platform] = {}
        elif line.startswith('|') and current_platform and '|-' not in line and '|}' not in line:
            cell = line[1:].strip()
            idx = len(results[current_platform])
            if idx < len(versions):
                results[current_platform][versions[idx]] = cell

    return results, versions

def parse_failure_list(content):
    """Parse failure list table and return list of failure rows."""
    failures = []
    lines = content.split('\n')
    in_failure_table = False
    current_failure = []
    
    for line in lines:
        if "Failure List" in line:
            in_failure_table = True
            continue
        if in_failure_table and "|}" in line:
            if current_failure and any(c.strip().lstrip('|').strip() for c in current_failure):
                failures.append(current_failure)
            break
        if not in_failure_table:
            continue
        
        # Skip header row
        if line.startswith('!'):
            continue
        
        if line.strip() == '|-':
            if current_failure and any(c.strip().lstrip('|').strip() for c in current_failure):
                failures.append(current_failure)
            current_failure = []
        elif line.startswith('|'):
            cell = line[1:].strip()
            if cell and cell != '?':
                current_failure.append(cell)
    
    return failures

def combine_files():
    new_ci = read_file(NEW_CI_FILE)
    old_ci = read_file(OLD_CI_FILE)
    
    new_results, new_versions = parse_matrix_simple(new_ci)
    old_results, old_versions = parse_matrix_simple(old_ci)
    
    # Parse failure lists
    new_failures = parse_failure_list(new_ci)
    old_failures = parse_failure_list(old_ci)
    
    # Define output columns order
    all_versions = ['PAC/trunk_tip', 'PAC/ED11.0_tip', 'ED10.0', 'ED9.0', 'ED8.0']
    platforms = ['rh-x64', 'rh-x86', 'win-x64', 'win-x86']
    
    def get_value(platform, version):
        if platform in new_results and version in new_results[platform]:
            return new_results[platform][version]
        if platform in old_results and version in old_results[platform]:
            return old_results[platform][version]
        return '~'
    
    def calc_total(platform):
        vals = [get_value(platform, v) for v in all_versions]
        fails = sum(1 for v in vals if v.isdigit() and int(v) > 0)
        if fails > 0:
            return str(sum(int(v) for v in vals if v.isdigit()))
        return 'P' if all(v in ('P', '~') for v in vals) else '?'
    
    output = f"""<!-- filepath: {COMBINED_FILE} -->
=={TODAY} PAC Combined Results (Harry Morley)==
===Results Matrix===
{{| class="wikitable"
|-
!Platform/Version
!PAC/trunk_tip
!PAC/ED11.0_tip
!ED10.0
!ED9.0
!ED8.0
!Total
"""
    
    for platform in platforms:
        vals = [get_value(platform, v) for v in all_versions]
        total = calc_total(platform)
        output += f"|-\n!{platform}\n"
        for v in vals:
            marker = '!' if v.isdigit() and int(v) > 0 else '|'
            output += f"{marker}{v}\n"
        total_marker = '!' if total.isdigit() and int(total) > 0 else '|'
        output += f"{total_marker}{total}\n"
    
    output += "|}\n"
    
    # Add Quick Summary
    output += """'''''Quick Summary:'''''
PLEASE MODIFY THIS WITH THE REQUIRED HIGHLIGHTS
"""
    
    # Add Combined Failure List
    output += """===Failure List===
{| class='wikitable'
!Failures
!Versions
!Platforms
!Age
!Machines
!Description
!Issue
!Assignee
"""
    
    all_failures = new_failures + old_failures
    
    if all_failures:
        for failure in all_failures:
            output += "|-\n"
            # Pad to 8 columns if needed
            while len(failure) < 8:
                failure.append("")
            for cell in failure[:8]:
                output += f"|{cell}\n"
    else:
        output += "|-\n"
    
    output += "|}\n"
    
    with open(COMBINED_FILE, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Combined results written to: {COMBINED_FILE}")

if __name__ == "__main__":
    combine_files()
