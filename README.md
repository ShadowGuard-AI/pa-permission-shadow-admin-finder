# pa-permission-shadow-admin-finder
Discovers users who, while not explicitly designated as administrators, possess a combination of permissions that effectively grants them administrative privileges. Compares user permissions against a profile of 'effective admin' permissions. An empty admin profile, and an empty or wrongly shaped user permissions file, are not-checked states that exit 1 with no findings list. The output file must not overwrite either input file, and a failed output write exits 1. - Focused on Tools for analyzing and assessing file system permissions

## Install
`git clone https://github.com/ShadowGuard-AI/pa-permission-shadow-admin-finder`
`cd pa-permission-shadow-admin-finder`
`pip install -r requirements.txt`

## Usage
`python3 main.py --user-permissions-file <file.json> --effective-admin-permissions-file <file.json> [--output-file <file>] [--log-level INFO]`

The user permissions file is JSON mapping each user to a list of paths, for example `{"alice": ["/etc/shadow", "/etc/sudoers"]}`. The effective admin permissions file is a JSON object with a `permissions` key holding the list of paths, for example `{"permissions": ["/etc/shadow", "/etc/sudoers"]}`. A sample run found `alice` as a shadow admin and wrote her name to the output file, exiting 0.

## Parameters
- `-h`: Show help message and exit
- `--user-permissions-file` (required): Path to the JSON file containing user permissions data.
- `--effective-admin-permissions-file` (required): Path to the JSON file containing the effective admin permissions profile.
- `--output-file` (optional): Path to the output file to save results (optional).
- `--log-level` (optional, default `INFO`): Set the logging level (default: INFO). Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL.

## License
Licensed under the MIT License, see LICENSE.
