# RAISE Search workflows

This directory includes definitions for workflows used to manage indexes for RAISE Search:

* `raise-search-index-daily` - A cron workflow which is used to automatically update `latest` with changes that occur on `main`
* `raise-search-index-template` - A workflow template that is used by a developer to index a specific content version as part of release

Once the workflow template is deployed, it can be invoked as follows:

```bash
$ argo -n raise submit --watch --from workflowtemplate/raise-search-index-template -p version="sha"
```
