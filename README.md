# GitHub Repository Insights

This GitHub Action generates insights for specified GitHub repositories, including views, clones, and referral sources.

## Inputs

- `repos` (required): Comma-separated list of repositories (e.g., `owner/repo1,owner/repo2`).
- `pat-token` (required): GitHub fine-grained personal access token with `administration:read` permission for the listed repositories.

## Outputs

This Action generates:

- Raw data in `insights/data/raw/`.
- Processed data in `insights/data/`.
- Charts in `insights/images/`.
- A Markdown report in `insights/README.md`.

## Example Usage

```yaml
name: Generate Insights

on:
  schedule:
    - cron: "0 0 * * *" # Runs daily
  workflow_dispatch:

jobs:
  generate-insights:
    runs-on: ubuntu-latest

    steps:
      - name: Generate GitHub Insights
        uses: emillg/github-repo-insights@v1
        with:
          repos: "owner/repo1,owner/repo2"
          pat-token: ${{ secrets.PAT_TOKEN }}
