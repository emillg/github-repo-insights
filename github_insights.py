import os
from datetime import datetime
import json
import shutil
from src.api import fetch_repo_views, fetch_repo_clones, fetch_repo_referrals
from src.data_processing import merge_data, save_data, preprocess_data

if __name__ == "__main__":
    pat_token = os.getenv("INPUT_PAT-TOKEN")
    repos = os.getenv("INPUT_REPOS").split(",")

    if not pat_token or not repos:
        raise ValueError("Both 'pat-token' and 'repos' must be provided.")

    DOCS_DIR = "docs"
    DATA_DIR = os.path.join(DOCS_DIR, "data")

    DOCSIFY_INDEX_HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>GitHub Repository Insights</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="description" content="Description">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify/lib/themes/buble.css" />
</head>
<body>
  <div id="app"></div>
  <script>
    window.$docsify = {
      name: 'GitHub Repository Insights',
      repo: 'emillg/github-repo-insights',
      subMaxLevel: 3
    };
  </script>
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/docsify.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/vega@6"></script>
  <script src="//cdn.jsdelivr.net/npm/vega-lite@6"></script>
  <script src="//cdn.jsdelivr.net/npm/vega-embed@7"></script>
  <script src="//cdn.jsdelivr.net/gh/jerCarre/vega_docsify@v1.1/lib/docsivega.js"></script>
</body>
</html>
"""

    if os.path.exists("insights/data/"):
        images_dir = os.path.join("insights", "images")
        if os.path.exists(images_dir):
            print("Deleting insights/images directory ...")
            shutil.rmtree(images_dir)
        print("Renaming 'insights' directory to 'docs' ...")
        os.rename("insights", "docs")
    else:
        os.makedirs(DATA_DIR, exist_ok=True)

    current_date = datetime.now().strftime("%Y%m%d")
    raw_data_dir = f"{DATA_DIR}/raw/{current_date}"
    os.makedirs(raw_data_dir, exist_ok=True)

    markdown_content = ""

    repo_views_summary = {}
    repo_clones_summary = {}

    try:
        for repo in repos:
            repo_safe_name = repo.replace("/", "_")

            # Fetch data from GitHub
            print(f"Fetching data for {repo}...")
            views_data = fetch_repo_views(repo, pat_token)
            clones_data = fetch_repo_clones(repo, pat_token)
            referrals_data = fetch_repo_referrals(repo, pat_token)

            # Save raw data
            print(f"Saving raw data for {repo}...")
            raw_views_file = f"{raw_data_dir}/{repo_safe_name}_views.json"
            raw_clones_file = f"{raw_data_dir}/{repo_safe_name}_clones.json"
            raw_referrals_file = f"{raw_data_dir}/{repo_safe_name}_referrals.json"
            save_data(views_data, raw_views_file)
            save_data(clones_data, raw_clones_file)
            save_data(referrals_data, raw_referrals_file)

            # Process and merge data
            print(f"Processing data for {repo}...")
            views_data_cleaned = {"views": views_data["views"]}
            clones_data_cleaned = {"clones": clones_data["clones"]}

            views_file = f"{DATA_DIR}/{repo_safe_name}_views.json"
            clones_file = f"{DATA_DIR}/{repo_safe_name}_clones.json"
            referrals_file = f"{DATA_DIR}/{repo_safe_name}_referrals.json"

            merged_views = merge_data(views_data_cleaned, views_file, "views")
            merged_clones = merge_data(
                clones_data_cleaned, clones_file, "clones")
            save_data(merged_views, views_file)
            save_data(merged_clones, clones_file)
            save_data(referrals_data, referrals_file)

            repo_views_summary[repo] = sum(item["count"]
                                           for item in merged_views["views"])
            repo_clones_summary[repo] = sum(item["count"]
                                            for item in merged_clones["clones"])

            # Preprocess data for plotting
            total_views = preprocess_data(merged_views["views"])
            unique_views = preprocess_data([
                {"timestamp": item["timestamp"], "count": item["uniques"]}
                for item in merged_views["views"]
            ])
            total_clones = preprocess_data(merged_clones["clones"])
            unique_clones = preprocess_data([
                {"timestamp": item["timestamp"], "count": item["uniques"]}
                for item in merged_clones["clones"]
            ])

            # Generate charts
            print(f"Generating charts for {repo}...")
            repo_views_chart = """
```vega
{{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 800,
  "title": "Visitors for {repo}",
  "data": {{
    "values": [
      {values_data}
    ]
  }},
  "mark": "line",
  "encoding": {{
    "x": {{
      "field": "date",
      "type": "temporal",
      "title": "Date",
      "scale": {{ "type": "utc" }},
      "axis": {{
        "format": "%Y-%m-%d",
        "labelAngle": -45,
        "labelOverlap": false,
        "tickCount": {{"interval": "day", "step": 1}}
      }}
    }},
    "y": {{"field": "value", "type": "quantitative", "title": "Views"}},
    "color": {{
      "field": "type",
      "type": "nominal",
      "legend": {{
        "title": null
      }}
    }},
    "tooltip": [
      {{ "field": "date", "type": "temporal", "title": "Date" }},
      {{ "field": "type", "type": "nominal", "title": "Metric" }},
      {{ "field": "value", "type": "quantitative", "title": "Value" }}
    ]
  }}
}}
```
""".format(
                repo=repo,
                values_data=",\n      ".join(
                    json.dumps(
                        {"date": item["timestamp"][:10], "type": "Total Views", "value": item["count"]})
                    for item in merged_views["views"])
                + ",\n      "
                + ",\n      ".join(
                    json.dumps(
                        {"date": item["timestamp"][:10], "type": "Unique Views", "value": item["uniques"]})
                    for item in merged_views["views"]))

            repo_clones_chart = """
```vega
{{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 800,
  "title": "Git Clones for {repo}",
  "data": {{
    "values": [
      {values_data}
    ]
  }},
  "mark": "line",
  "encoding": {{
    "x": {{
      "field": "date",
      "type": "temporal",
      "title": "Date",
      "scale": {{ "type": "utc" }},
      "axis": {{
        "format": "%Y-%m-%d",
        "labelAngle": -45,
        "labelOverlap": false,
        "tickCount": {{"interval": "day", "step": 1}}
      }}
    }},
    "y": {{"field": "value", "type": "quantitative", "title": "Clones"}},
    "color": {{
      "field": "type",
      "type": "nominal",
      "legend": {{
        "title": null
      }}
    }},
    "tooltip": [
      {{ "field": "date", "type": "temporal", "title": "Date" }},
      {{ "field": "type", "type": "nominal", "title": "Metric" }},
      {{ "field": "value", "type": "quantitative", "title": "Value" }}
    ]
  }}
}}
```
""".format(
                repo=repo,
                values_data=",\n      ".join(
                    json.dumps(
                        {"date": item["timestamp"][:10], "type": "Total Clones", "value": item["count"]})
                    for item in merged_clones["clones"]
                )
                + ",\n      "
                + ",\n      ".join(
                    json.dumps({"date": item["timestamp"][:10],
                                "type": "Unique Clones", "value": item["uniques"]})
                    for item in merged_clones["clones"]
                )
            )

            # Generate Markdown content
            print(f"Generating Markdown for {repo}...")
            repo_url = f"https://github.com/{repo}"
            markdown_content += """### {repo}

[![GitHub Repo](https://img.shields.io/badge/-Repository-white?logo=github&logoColor=181717&style=social)]({repo_url})&nbsp;
[![GitHub Stars](https://img.shields.io/github/stars/{repo}?style=social)]({repo_url}/stargazers)&nbsp;
[![GitHub Forks](https://img.shields.io/github/forks/{repo}?style=social)]({repo_url}/network/members)&nbsp;
[![GitHub Watchers](https://img.shields.io/github/watchers/{repo}?style=social)]({repo_url}/watchers)

{repo_views_chart}
{repo_clones_chart}
""".format(
                repo=repo,
                repo_url=repo_url,
                repo_views_chart=repo_views_chart,
                repo_clones_chart=repo_clones_chart
            )

            markdown_content += "| Referral Source | Views | Unique Visitors |\n"
            markdown_content += "|-|-|-|\n"
            for referral in referrals_data:
                markdown_content += f"| {referral['referrer']} | {referral['count']} | {referral['uniques']} |\n"
            markdown_content += "\n"

        print("Generating top 10 repositories charts...")
        sorted_views = sorted(repo_views_summary.items(),
                              key=lambda x: x[1], reverse=True)[:10]
        sorted_clones = sorted(repo_clones_summary.items(),
                               key=lambda x: x[1], reverse=True)[:10]

        print("Generating chart for top 10 repositories by views...")
        view_values = [item[1] for item in sorted_views]
        overview_views_chart = """
```vega
{{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 800,
  "height": 300,
  "title": "Top 10 Repositories by Visitors",
  "data": {{
    "values": [
      {values_data}
    ]
  }},
  "mark": {{
    "type": "bar",
    "color": "#ff7f0e"
  }},
  "encoding": {{
    "y": {{"field": "repository", "type": "nominal", "title": "Repository", "sort": "-x"}},
    "x": {{"field": "views", "type": "quantitative", "title": "Total Views"}}
  }}
}}
```
""".format(
            values_data=", ".join(
                f'{{"repository": "{repo.split("/")[-1]}", "views": {views}}}'
                for repo, views in sorted_views
            )
        )

        clone_values = [item[1] for item in sorted_clones]
        print("Generating chart for top 10 repositories by clones...")
        overview_clones_chart = """
```vega
{{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 800,
  "height": 300,
  "title": "Top 10 Repositories by Git Clones",
  "data": {{
    "values": [
      {values_data}
    ]
  }},
  "mark": {{
    "type": "bar",
    "color": "#ff7f0e"
  }},
  "encoding": {{
    "y": {{"field": "repository", "type": "nominal", "title": "Repository", "sort": "-x"}},
    "x": {{"field": "clones", "type": "quantitative", "title": "Total Clones"}}
  }}
}}
```
""".format(
            values_data=", ".join(
                f'{{"repository": "{repo.split("/")[-1]}", "clones": {clones}}}'
                for repo, clones in sorted_clones
            )
        )

        # Add the top 10 charts to the beginning of the Markdown content
        overview_content = """# Insights

## Overview
{overview_views_chart}
{overview_clones_chart}
""".format(
            overview_views_chart=overview_views_chart,
            overview_clones_chart=overview_clones_chart
        )

        breakdown_content = "## Repository Breakdown\n\n"

        # Combine overview and per-repo content
        markdown_content = overview_content + breakdown_content + markdown_content

        with open(f"{DOCS_DIR}/README.md", "w") as markdown_file:
            markdown_file.write(markdown_content)

        print("Generating index.html for Docsify...")
        with open(f"{DOCS_DIR}/index.html", "w") as mkdocs_file:
            mkdocs_file.write(DOCSIFY_INDEX_HTML_CONTENT)

        print("Insights generated successfully!")

    except Exception as e:
        print(f"Error: {e}")
