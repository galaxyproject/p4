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
It finds that the PR is:

- open
- it doesn't contain `[PROCEDURES]` or `[WIP]`,
- and that it has one or more `:+1:` votes (+1 is accepted if on a line by itself)
- that the PR was created more than a day ago

when all these conditions pass, the bot tags the PR

```log
(env)hxr@leda:~/work/p4$ python process.py
INFO:root:Registered PullRequestFilter Tag popular, but untriaged PRs
INFO:root:Locating closed PRs
INFO:root:Locating open PRs
DEBUG:root:[1] Cache says: 2016-01-13 21:31:03 last updated at 2016-01-13 22:25:51
INFO:root:Found 1 PRs to examine
DEBUG:root:Evaluating 1
DEBUG:root: [Check Procedures PRs for mergability]
DEBUG:root:     state, open => True
DEBUG:root:     title_contains__not, [PROCEDURES] => True
DEBUG:root:     title_contains__not, [WIP] => True
DEBUG:root:     created_at__ge, 'relative::24 hours ago' => True
DEBUG:root:     plus__ge, 1 => True
INFO:root:Matched 1
INFO:root:Executing action
```

The second time around our state is stored in the database, so we fail to find
any PRs that need comments.

```
(env)hxr@leda:~/work/p4$ python process.py
INFO:root:Registered PullRequestFilter Tag popular, but untriaged PRs
INFO:root:Locating closed PRs
INFO:root:Locating open PRs
DEBUG:root:[1] Cache says: 2016-01-13 22:25:51 last updated at 2016-01-13 22:25:51
INFO:root:Found 0 PRs to examine
```
