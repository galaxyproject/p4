# Proper Prior PR Planning

[![Build Status](https://travis-ci.org/erasche/p4.svg)](https://travis-ci.org/erasche/p4)

Simple bot to comment on GitHub repositories to help guide repository
maintenance. This includes things like ensuring enough members of the core team
+1 a pull request, and otherwise help ensure that procedures are consistently
followed for merging of PRs.

## How it works

- run the script as regularly as seems reasonable (and stays within your GH API
  limits)
- the script fetches all pull requests for a repository
- this data is compared against a database
- PRs which have updated since the last run are checked individually
- various filters are applied to the PR, with user-defined behaviour resulting
  if the PR matches a filter
- if a PR passes all filters, one or more actions is executed.
- the database is updated


## Example Run

Our first run we watch the bot find a PR (#1), and evaluate a number of states.
It finds that the PR is open, it doesn't contain `[PROCEDURES]`, and that it
has one or more `:+1:` votes (emoji required)

```log
(env)hxr@leda:~/work/p4$ python process.py
INFO:root:Registered PullRequestFilter Check PRs to dev for mergability
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): api.github.com
DEBUG:requests.packages.urllib3.connectionpool:"GET /repos/erasche/gx-package-caching/pulls?per_page=100&state=open&page=1 HTTP/1.1" 200 None
INFO:root:Built PullRequest #1 Testing change for p4
DEBUG:root:Found 1 PRs to examine
DEBUG:root:[Check PRs to dev for mergability] Evaluating state open for <#1 "Testing change for p4" by @erasche>
DEBUG:root:[Check PRs to dev for mergability] Evaluating title_contains__not [PROCEDURES] for <#1 "Testing change for p4" by @erasche>
DEBUG:root:[Check PRs to dev for mergability] Evaluating plus__ge 1 for <#1 "Testing change for p4" by @erasche>
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): api.github.com
DEBUG:requests.packages.urllib3.connectionpool:"GET /repos/erasche/gx-package-caching/issues/1/comments?per_page=100&page=1 HTTP/1.1" 200 None
DEBUG:root:[Check PRs to dev for mergability] Evaluating to_branch master for <#1 "Testing change for p4" by @erasche>
INFO:root:Matched Check PRs to dev for mergability
INFO:root:Executing action
```

The second time around our state is stored in the database, so we fail to find
any PRs that need comments.

```
(env)hxr@leda:~/work/p4$ python process.py
INFO:root:Registered PullRequestFilter Check PRs to dev for mergability
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): api.github.com
DEBUG:requests.packages.urllib3.connectionpool:"GET /repos/erasche/gx-package-caching/pulls?per_page=100&state=open&page=1 HTTP/1.1" 200 None
2015-09-15 02:07:00 2015-09-15 02:07:00
DEBUG:root:Found 0 PRs to examine
```
