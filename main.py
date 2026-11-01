import argparse
import logging
import os
import sys
import json

# Attempt to import dependencies, exit if not found (as per requirements)
try:
    from rich.console import Console
    from rich.table import Column, Table
except ImportError as e:
    print(f"Error: Missing dependency: {e}. Please install using pip.")
    sys.exit(1)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the CLI.
    """
    parser = argparse.ArgumentParser(description="Discover users with shadow admin privileges based on file system permissions.")
    parser.add_argument("--user-permissions-file", required=True, help="Path to the JSON file containing user permissions data.")
    parser.add_argument("--effective-admin-permissions-file", required=True, help="Path to the JSON file containing the effective admin permissions profile.")
    parser.add_argument("--output-file", help="Path to the output file to save results (optional).")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level (default: INFO).")

    return parser.parse_args()


def load_permissions_data(file_path):
    """
    Loads permissions data from a JSON file.
    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The permissions data as a dictionary.  Returns None on error.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None


def find_shadow_admins(user_permissions, effective_admin_permissions):
    """
    Identifies users who possess effective admin permissions.

    Args:
        user_permissions (dict): A dictionary containing user permissions data.
                                  Expected format: {"user1": ["/path/to/file1", "/path/to/file2"], ...}
        effective_admin_permissions (list): A list of permissions that define an effective admin.

    Returns:
        list: A list of usernames who are considered shadow admins.
    """
    shadow_admins = []

    if not isinstance(user_permissions, dict):
        logging.error("Invalid user permissions data. Expected a dictionary.")
        return []

    if not isinstance(effective_admin_permissions, list):
        logging.error("Invalid effective admin permissions data. Expected a list.")
        return []

    for user, permissions in user_permissions.items():
        if not isinstance(permissions, list):
            logging.warning(f"User {user} has invalid permissions format. Skipping.")
            continue

        # The test is exact string membership. I do no path tidying, so
        # the same file written with a trailing slash, a relative form,
        # or different case in the two input files does not match and
        # the user is missed.
        # all() on an empty profile would name every user, which is why
        # main refuses an empty profile before this function ever runs.
        # That guard is load bearing, not decoration.
        if all(perm in permissions for perm in effective_admin_permissions):
            shadow_admins.append(user)
            logging.info(f"User {user} identified as a shadow admin.")

    return shadow_admins


def save_results(results, output_file):
    """
    Saves the shadow admin results to a file.

    Args:
        results (list): A list of shadow admin usernames.
        output_file (str): The path to the output file.

    Returns:
        True when the file was written, False on failure.
    """
    try:
        with open(output_file, "w") as f:
            for user in results:
                f.write(f"{user}\n")
        logging.info(f"Results saved to: {output_file}")
        return True
    except Exception as e:
        logging.error(f"Error saving results to {output_file}: {e}")
        return False


def display_results(results):
    """
    Displays the shadow admin results in a table format.

    Args:
        results (list): A list of shadow admin usernames.
    """
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Shadow Admin User", style="cyan")

    if not results:
        console.print("[bold yellow]No shadow admins found.[/]")
        return

    for user in results:
        table.add_row(user)

    console.print(table)

def main():
    """
    Main function to execute the shadow admin finder tool.
    """
    args = setup_argparse()

    # Set log level
    logging.getLogger().setLevel(args.log_level.upper())

    user_permissions_data = load_permissions_data(args.user_permissions_file)
    effective_admin_permissions_data = load_permissions_data(args.effective_admin_permissions_file)


    if user_permissions_data is None or effective_admin_permissions_data is None:
        logging.error("Failed to load permissions data. Exiting.")
        sys.exit(1)

    # Validate structure of permissions data
    if not isinstance(effective_admin_permissions_data, dict):
        logging.error("Invalid format for effective admin permissions. Expected an object with a 'permissions' key. Exiting.")
        print("Error: Effective admin permissions data must be an object with a 'permissions' key. Nothing was checked.")
        sys.exit(1)
    effective_admin_permissions = effective_admin_permissions_data.get("permissions") #Example Format {"permissions":["/path/to/file1", "/path/to/file2"]}
    if not isinstance(effective_admin_permissions, list):
        logging.error("Invalid format for effective admin permissions. Expected list of permissions in a 'permissions' key.  Exiting.")
        sys.exit(1)

    if len(effective_admin_permissions) == 0:
        logging.error("Effective admin profile is empty. Nothing was checked.")
        print("Error: Effective admin profile is empty. Nothing was checked.")
        sys.exit(1)

    if not isinstance(user_permissions_data, dict) or len(user_permissions_data) == 0:
        logging.error("User permissions data must be a non-empty object. Nothing was checked.")
        print("Error: User permissions data must be a non-empty object. Nothing was checked.")
        sys.exit(1)

    # The overwrite check runs before any result exists and compares
    # resolved paths, so a symlink or a relative spelling of an input
    # file is still caught. Saving happens before the table prints, and
    # a save failure exits without ever showing the found names on
    # screen.
    if args.output_file:
        output_resolved = os.path.realpath(args.output_file)
        if output_resolved in (os.path.realpath(args.user_permissions_file), os.path.realpath(args.effective_admin_permissions_file)):
            logging.error("Output file must not overwrite an input file.")
            print("Error: Output file must not overwrite an input file.")
            sys.exit(1)

    shadow_admins = find_shadow_admins(user_permissions_data, effective_admin_permissions)

    if args.output_file:
        if not save_results(shadow_admins, args.output_file):
            print("Error: Results not saved: writing the output file failed.")
            sys.exit(1)

    display_results(shadow_admins)


# Example usage (can be removed or kept as a comment)
# Create dummy JSON files for testing
# with open("user_permissions.json", "w") as f:
#     json.dump({"user1": ["/etc/shadow", "/etc/sudoers", "/var/log/auth.log"], "user2": ["/home/user2/file1", "/home/user2/file2"]}, f)
# with open("effective_admin_permissions.json", "w") as f:
#     json.dump({"permissions":["/etc/shadow", "/etc/sudoers"]}, f)


if __name__ == "__main__":
    main()