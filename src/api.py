import requests


def fetch_repo_views(repo, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    views_url = f"https://api.github.com/repos/{repo}/traffic/views"
    response = requests.get(views_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching views: {response.text}")
    return response.json()


def fetch_repo_clones(repo, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    clones_url = f"https://api.github.com/repos/{repo}/traffic/clones"
    response = requests.get(clones_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching clones: {response.text}")
    return response.json()


def fetch_repo_referrals(repo, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    referrals_url = f"https://api.github.com/repos/{repo}/traffic/popular/referrers"
    response = requests.get(referrals_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching referrals: {response.text}")
    return response.json()
