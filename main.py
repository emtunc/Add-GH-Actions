import datetime
import time
from github import Github

GITHUB = Github("Your Personal Access Token here")  # Personal Access Token - repo scopes is all that is required
ORGANIZATION = "Your Github Organization name here"
CODEQL_ANALYSIS_FILE = '.github/workflows/codeql-analysis.yml'
CODEQL_CONFIG_FILE = '.github/codeql-config.yml'
TODAYS_DATETIME = datetime.datetime.now()
TARGET_BRANCH = 'security-static-code-analysis-' + TODAYS_DATETIME.strftime("%Y-%m-%d-%H-%M-%S")
SOURCE_BRANCH = 'master'
PR_TITLE = 'Security - Static Code Analysis (CodeQL)'
PR_BODY = '''
Adding Static Code Analysis scanning to Github repositories to help find potential vulnerabilities in code.
This is a feature of _[Github Advanced Security](https://github.com/features/security)_

Only scans on push to master and on a once-a-week schedule. Builds are not blocked.

:police_officer: **This is an automated PR: If you are happy with the PR, please approve and merge it** :police_officer:
'''


def configure_codeql():
    output_urls = open("output", 'a')
    output_urls.write(TODAYS_DATETIME.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    with open("codeql-analysis.yml", "r") as actions_file:
        codeql_analysis = actions_file.read()
    with open("codeql-config.yml", "r") as actions_config:
        codeql_config = actions_config.read()
    with open("repos.list", "r") as file:
        repo_list = file.read().splitlines()
        print(f"INFO: {len(repo_list)} repositories to be processed. You have 5 seconds to change your mind.")
        time.sleep(5)

    for repository in repo_list:
        try:
            print(f"INFO: {repository} - Processing")
            repo = GITHUB.get_repo(ORGANIZATION + "/" + repository)
            sb = repo.get_branch(SOURCE_BRANCH)
            repo.create_git_ref(ref='refs/heads/' + TARGET_BRANCH, sha=sb.commit.sha)

            # Check whether the file already exists. If so, use the update method otherwise adding will fail
            codeql_analysis_file = does_file_exist(repo, CODEQL_ANALYSIS_FILE)
            if codeql_analysis_file[0]:
                print(f"INFO: {repository} - CodeQL Analysis file already exists. Overwriting...")
                repo.update_file(codeql_analysis_file[1].path, "Updating CodeQL workflow", codeql_analysis,
                                 codeql_analysis_file[1].sha, branch=TARGET_BRANCH)
            else:
                repo.create_file(CODEQL_ANALYSIS_FILE, "Adding CodeQL workflow", codeql_analysis, branch=TARGET_BRANCH)

            codeql_config_file = does_file_exist(repo, CODEQL_CONFIG_FILE)
            if codeql_config_file[0]:
                print(f"INFO: {repository} - CodeQL Config file already exists. Overwriting...")
                repo.update_file(codeql_config_file[1].path, "Updating CodeQL config file", codeql_config,
                                 codeql_config_file[1].sha, branch=TARGET_BRANCH)
            else:
                repo.create_file(CODEQL_CONFIG_FILE, "Adding CodeQL config file", codeql_config, branch=TARGET_BRANCH)

            pr = repo.create_pull(title=PR_TITLE, body=PR_BODY, head=TARGET_BRANCH, base=SOURCE_BRANCH)
            output_urls.write(f"{pr.html_url} \n")
            print(f"INFO: {repository} - PR successfully created. PR URL written to file.")

        except Exception as error:
            print(f"ERROR: {repository} failed with error: {error}")
            output_urls.write(f"ERROR: {repository} failed with error: {error} \n")

    output_urls.close()


def does_file_exist(repo, file):
    """
    Checks whether the file we are trying to add already exists. If so, return True and the contents object.
    The file path and sha hash is required if we want to update it.
    If the file does not already exist, return False and continue to use the _add_ method.
    """
    try:
        contents = repo.get_contents(file, ref="master")
        if contents:
            return True, contents
    except:
        return False, None


def write_repository_list_to_file():
    """
    Get all private repos in the organisation then write the repository name to the output file if:
    - Repo main language is {language_filter}, and
    - Repo has been updated in the last {days_last_updated} days
    """
    days_last_updated = 180
    language_filter = 'Java'
    try:
        date_filter = TODAYS_DATETIME - datetime.timedelta(days=days_last_updated)
        with open("repos.list", "a") as repository_list:
            for repo in GITHUB.get_organization(ORGANIZATION).get_repos(type="private", sort="updated", direction="desc"):
                if repo.language == language_filter and repo.updated_at > date_filter:
                    repository_list.write(repo.name + "\n")
    except Exception as error:
        print(f"ERROR: Check your PAT and that you are targeting an org and not your GH username. Error: {error}")
