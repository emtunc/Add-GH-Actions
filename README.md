# Automate Adding Github Actions to Repos
Quick and dirty Python (3.7) script which I created to automate the process of adding CodeQL (Github Advanced Security) workflows and config files to lots of repositories in a Github org.

There's no reason why you couldn't re-purpose this to add other files.

Features:

  * Filter repositories you want to add the files to by programming language (default: Java) and last updated date (default: 6 months)
  * Add or update (if the files already exist on the master branch) the files and create a PR on a newly created branch
  * Should be faster than other scripts out there as we don't need to clone the repo locally and push it back up
  
## Building

The script has been developed, tested and confirmed working on Python 3.7.

#### Linux with virtualenv

  * `git clone https://github.com/emtunc/Add-GH-Actions`
  * `virtualenv venv`
  * `source venv/bin/activate`
  * `pip install -r REQUIREMENTS.txt`

## Usage

I haven't made this in to a proper script with CLI flags/switches because, YOLO.

Edit main.py and add your own Personal Access Token (PAT) to the `GITHUB` variable and your organization name to the `ORGANIZATION` variable.

  * Write list of repos to a file. Default filter is Java repos last updated in the last 6 months (edit the `write_repository_list_to_file` function in the script if you want to change this):
  
 ```python3 -c 'from main import *; write_repository_list_to_file()'```

  * Add the files to all repos discovered in `repos.list`

 ```python3 -c 'from main import *; configure_codeql()'```