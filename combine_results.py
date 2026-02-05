import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_UNDERSCORE = datetime.now().strftime("%Y_%m_%d")

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

# Report types to process
REPORT_TYPES = ['CONF', 'FULL', 'IPIC', 'PAC', 'PRIVATE', 'WEEKEND']

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
    """Parse the results matrix, handling both | and ! prefixed values."""
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
            current_platform = None  # Reset platform on row separator
            continue
        
        stripped = line.strip()
        
        # Check if this is a platform row (starts with ! and is a known platform)
        if stripped.startswith('!') and 'Platform' not in stripped and 'Total' not in stripped:
            platform_raw = stripped[1:].strip().lower()
            normalized = PLATFORM_MAP.get(platform_raw, platform_raw)
            # Only treat as platform if it matches known platforms
            if normalized in ['rh-x64', 'rh-x86', 'win-x64', 'win-x86']:
                current_platform = normalized
                results[current_platform] = {}
                continue
        
        # Data cell - can start with | or ! (! indicates failure count)
        if current_platform and (stripped.startswith('|') or stripped.startswith('!')):
            if '|-' in stripped or '|}' in stripped:
                continue
            cell = stripped[1:].strip()
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

def combine_files_for_type(report_type):
    """Combine CI and OldCI files for a specific report type."""
    new_ci_file = os.path.join(REPORTS_DIR, f"CI_Status_Results_{report_type}_{TODAY}.md")
    old_ci_file = os.path.join(REPORTS_DIR, f"OldCI_Status_Results_{report_type}_{TODAY}.md")
    combined_file = os.path.join(REPORTS_DIR, f"CI_Combined_Results_{report_type}_{TODAY_UNDERSCORE}.md")
    
    # Check if new CI file exists (required)
    if not os.path.exists(new_ci_file):
        print(f"Skipping {report_type}: No CI_Status_Results_{report_type}_{TODAY}.md found")
        return False
    
    new_ci = read_file(new_ci_file)
    old_ci = read_file(old_ci_file)  # May be empty if file doesn't exist
    
    new_results, new_versions = parse_matrix_simple(new_ci)
    old_results, old_versions = parse_matrix_simple(old_ci)
    
    # Parse failure lists
    new_failures = parse_failure_list(new_ci)
    old_failures = parse_failure_list(old_ci)
    
    # Combine versions dynamically: new CI versions first, then old CI versions (no duplicates)
    all_versions = []
    for v in new_versions:
        if v not in all_versions:
            all_versions.append(v)
    for v in old_versions:
        if v not in all_versions:
            all_versions.append(v)
    
    platforms = ['rh-x64', 'rh-x86', 'win-x64', 'win-x86']
    
    def get_value(platform, version):
        if platform in new_results and version in new_results[platform]:
            return new_results[platform][version]
        if platform in old_results and version in old_results[platform]:
            return old_results[platform][version]
        return '~'
    
    def calc_total(platform):
        vals = [get_value(platform, v) for v in all_versions]
        # Sum numeric values
        numeric_sum = 0
        has_numeric = False
        for v in vals:
            try:
                num = int(v)
                if num > 0:
                    numeric_sum += num
                    has_numeric = True
            except ValueError:
                pass
        if has_numeric:
            return str(numeric_sum)
        return 'P' if all(v in ('P', '~') for v in vals) else '?'
    
    # Build header with dynamic versions
    output = f"""<!-- filepath: {combined_file} -->
=={TODAY} {report_type} Combined Results (Harry Morley)==
===Results Matrix===
{{| class="wikitable"
|-
!Platform/Version
"""
    for v in all_versions:
        output += f"!{v}\n"
    output += "!Total\n"
    
    for platform in platforms:
        vals = [get_value(platform, v) for v in all_versions]
        total = calc_total(platform)
        output += f"|-\n!{platform}\n"
        for v in vals:
            try:
                marker = '!' if int(v) > 0 else '|'
            except ValueError:
                marker = '|'
            output += f"{marker}{v}\n"
        try:
            total_marker = '!' if int(total) > 0 else '|'
        except ValueError:
            total_marker = '|'
        output += f"{total_marker}{total}\n"
    
    # Add Total row
    def calc_version_total(version):
        """Calculate total for a specific version across all platforms."""
        total_sum = 0
        has_numeric = False
        for platform in platforms:
            val = get_value(platform, version)
            try:
                num = int(val)
                if num > 0:
                    total_sum += num
                    has_numeric = True
            except ValueError:
                pass
        if has_numeric:
            return str(total_sum)
        return 'P' if all(get_value(p, version) in ('P', '~') for p in platforms) else '?'
    
    output += "|-\n!Total\n"
    grand_total = 0
    has_grand_numeric = False
    for v in all_versions:
        ver_total = calc_version_total(v)
        try:
            marker = '!' if int(ver_total) > 0 else '|'
            grand_total += int(ver_total)
            has_grand_numeric = True
        except ValueError:
            marker = '|'
        output += f"{marker}{ver_total}\n"
    
    # Grand total (sum of all version totals)
    if has_grand_numeric:
        grand_marker = '!' if grand_total > 0 else '|'
        output += f"{grand_marker}{grand_total}\n"
    else:
        output += "|P\n"
    
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
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Combined results written to: {combined_file}")
    return True

def combine_files():
    """Process all report types."""
    print(f"Processing reports for date: {TODAY}")
    print(f"Looking in directory: {REPORTS_DIR}")
    print("-" * 50)
    
    processed = 0
    for report_type in REPORT_TYPES:
        if combine_files_for_type(report_type):
            processed += 1
    
    print("-" * 50)
    print(f"Processed {processed} report type(s)")

if __name__ == "__main__":
    combine_files()
