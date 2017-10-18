Contributing to cookbook-elasticsearch
======================================

### Workflow for contributing

1. Create a branch directly in this repo or a fork (if you don't have push access). Please name branches within this repository `<fix type>/<description>`. For example, something like feature/install_from_deb.

1. Create an issue or open a PR. If you aren't sure your PR will solve the issue, or may be controversial, we commend opening an issue separately and linking to it in your PR, so that if the PR is not accepted, the issue will remain and be tracked.

1.  Close (and reference) issues by the `closes #XXX` or `fixes #XXX` notation in the commit message. Please use a descriptive, useful commit message that could be used to understand why a particular change was made.

1. Keep pushing commits to the initial branch, `--amend`-ing if necessary. Please don't mix fixing unrelated issues in a single branch.

1. Create a changelog entry as per [Keep A Changelog](http://keepachangelog.com/). You should only be putting new stuff under `## [Unreleased]` and should not concern yourself with bumping the version and dates as this will be done when releasing changes. When you need to have a change that will break things it needs to be called out with a `### Breaking Changes` as opposed to a more common header such as `### Added, ### Fixed, ### Changed`. This helps maintainers evaluate what the appropriate version bump should be as there could be changes that are not immediately released.

1. When everything is ready for merge, clean up the branch (rebase with master to synchronize, squash, edit commits, etc) to prepare for it to be merged. Unless you have meaningful history it should be a single commit. Prefer a rebase to a merge for brining in changes that have been committed to upstream master.

### Merging contributions

1. After reviewing commits for documentation, passing CI tests, and good descriptive commit messages, merge it with either "squash and merge" or "rebase and merge" do not use the
"merge pull request" as it does not do a fast forward first.


### Releasing

1. Create/update the changelog entries and evaluate the type of release.
1. create a git release with something like hub, example: `hub release create vMajor.Minor.patch`
