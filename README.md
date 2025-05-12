# GitHub Repository Insights

This GitHub Action collects insights data from GitHub for specified repositories, including views, clones, and referral sources. It saves raw and merged data in the repository and generates Markdown reports for GitHub Pages, enabling long-term tracking beyond GitHub's 14-day limitation.

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
    - cron: "0 1 * * *" # Runs daily
  workflow_dispatch:

jobs:
  generate-insights:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub Insights
        uses: emillg/github-repo-insights@v1
        with:
          repos: "owner/repo1,owner/repo2"
          pat-token: ${{ secrets.PAT_TOKEN }}

      # Commit and push the generated insights to the 'insights' branch
      - name: Commit and push insights
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git checkout -B insights
          git add insights/
          git commit -m "Update GitHub Insights"
          git push -u origin insights --force
```

## GitHub Pages

To make the generated insights accessible as a GitHub Pages site:

1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Pages**.
3. Under **Source**, select the `insights` branch and set the directory to `/` (root).
4. Click **Save**.

Once enabled, your insights will be available at `https://<your-username>.github.io/<repository-name>/insights`.

## Local Testing

You can test this Action locally:

```bash
pip install -r requirements.txt

env INPUT_PAT-TOKEN=<your_personal_access_token> INPUT_REPOS="owner/repo1,owner/repo2" python github_insights.py
```
