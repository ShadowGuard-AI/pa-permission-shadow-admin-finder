# pa-permission-shadow-admin-finder
Discovers users who, while not explicitly designated as administrators, possess a combination of permissions that effectively grants them administrative privileges. Compares user permissions against a profile of 'effective admin' permissions. An empty admin profile, and an empty or wrongly shaped user permissions file, are not-checked states that exit 1 with no findings list. The output file must not overwrite either input file, and a failed output write exits 1. - Focused on Tools for analyzing and assessing file system permissions

## Install
`git clone https://github.com/ShadowStrikeHQ/pa-permission-shadow-admin-finder`

## Usage
`./pa-permission-shadow-admin-finder [params]`

## Parameters
- `-h`: Show help message and exit
- `--user-permissions-file`: Path to the JSON file containing user permissions data.
- `--effective-admin-permissions-file`: Path to the JSON file containing the effective admin permissions profile.
- `--output-file`: No description provided
- `--log-level`: No description provided

## License
Copyright (c) ShadowStrikeHQ
