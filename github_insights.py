import os
from datetime import datetime
from src.api import fetch_repo_views, fetch_repo_clones, fetch_repo_referrals
from src.data_processing import merge_data, save_data, preprocess_data
from src.plotting import plot_line_chart, plot_bar_chart

if __name__ == "__main__":
    pat_token = os.getenv("INPUT_PAT-TOKEN")
    repos = os.getenv("INPUT_REPOS").split(",")

    if not pat_token or not repos:
        raise ValueError("Both 'pat-token' and 'repos' must be provided.")

    os.makedirs("insights/images", exist_ok=True)
    os.makedirs("insights/data", exist_ok=True)
    current_date = datetime.now().strftime("%Y%m%d")
    raw_data_dir = f"insights/data/raw/{current_date}"
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

            views_file = f"insights/data/{repo_safe_name}_views.json"
            clones_file = f"insights/data/{repo_safe_name}_clones.json"
            referrals_file = f"insights/data/{repo_safe_name}_referrals.json"

            merged_views = merge_data(views_data_cleaned, views_file, "views")
            merged_clones = merge_data(
                clones_data_cleaned, clones_file, "clones")
            save_data(merged_views, views_file)
            save_data(merged_clones, clones_file)
            save_data(referrals_data, referrals_file)

            total_views = sum(item["count"] for item in merged_views["views"])
            total_clones = sum(item["count"]
                               for item in merged_clones["clones"])
            repo_views_summary[repo] = total_views
            repo_clones_summary[repo] = total_clones

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
            views_chart_filename = f"insights/images/{repo_safe_name}_views.png"
            clones_chart_filename = f"insights/images/{repo_safe_name}_clones.png"

            plot_line_chart(
                data_series=[total_views, unique_views],
                title=f"Visitors for {repo}",
                ylabel="Views",
                labels=["Total Views", "Unique Views"],
                filename=views_chart_filename
            )

            plot_line_chart(
                data_series=[total_clones, unique_clones],
                title=f"Git Clones for {repo}",
                ylabel="Clones",
                labels=["Total Clones", "Unique Clones"],
                filename=clones_chart_filename
            )

            # Generate Markdown content
            print(f"Generating Markdown for {repo}...")
            markdown_content += f"### {repo}\n\n"

            # Add charts side by side using a Markdown table
            markdown_content += (
                f"| ![Visitors Chart for {repo}](images/{repo_safe_name}_views.png) "
                f"| ![Git Clones Chart for {repo}](images/{repo_safe_name}_clones.png) |\n"
                f"|-|-|\n\n"
            )

            markdown_content += "| Referral Source | Views | Unique Visitors |\n"
            markdown_content += "|-|-|-|\n"
            for referral in referrals_data:
                markdown_content += f"| {referral['referrer']} | {referral['count']} | {referral['uniques']} |\n"
            markdown_content += "\n"

        # Generate a bar chart for the top 10 repositories by views
        print("Generating top 10 repositories charts...")
        sorted_views = sorted(repo_views_summary.items(),
                              key=lambda x: x[1], reverse=True)[:10]
        sorted_clones = sorted(repo_clones_summary.items(),
                               key=lambda x: x[1], reverse=True)[:10]

        # Top 10 by views
        view_categories = [item[0] for item in sorted_views]
        view_values = [item[1] for item in sorted_views]
        top_views_chart_filename = "insights/images/top_10_repos_views.png"
        plot_bar_chart(
            categories=view_categories,
            values=view_values,
            title="Top 10 Repositories by Visitors",
            xlabel="Total Views",
            ylabel="Repositories",
            filename=top_views_chart_filename
        )

        # Top 10 by clones
        clone_categories = [item[0] for item in sorted_clones]
        clone_values = [item[1] for item in sorted_clones]
        top_clones_chart_filename = "insights/images/top_10_repos_clones.png"
        plot_bar_chart(
            categories=clone_categories,
            values=clone_values,
            title="Top 10 Repositories by Git Clones",
            xlabel="Total Clones",
            ylabel="Repositories",
            filename=top_clones_chart_filename
        )

        # Add the top 10 charts to the beginning of the Markdown content
        overview_content = "# GitHub Insights\n\n"
        overview_content += "## Overview\n\n"
        overview_content += (
            "| ![Top 10 Repositories by Views](images/top_10_repos_views.png) "
            "| ![Top 10 Repositories by Clones](images/top_10_repos_clones.png) |\n"
            "|-|-|\n\n"
        )

        breakdown_content = "## Repository Breakdown\n\n"

        # Combine overview and per-repo content
        markdown_content = overview_content + breakdown_content + markdown_content

        with open("insights/README.md", "w") as markdown_file:
            markdown_file.write(markdown_content)

        print("Insights generated successfully!")

    except Exception as e:
        print(f"Error: {e}")
