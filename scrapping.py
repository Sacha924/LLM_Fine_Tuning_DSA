import requests
import re
from html import unescape

def fetch_leetcode_question_content(csrf_token, leetcode_session, title_slug):
    """
    Fetch the content of a LeetCode question based on its title slug.

    :param csrf_token: CSRF token for the session
    :param leetcode_session: LEETCODE_SESSION token
    :param title_slug: Title slug of the LeetCode question
    :return: Cleaned content of the question
    """

    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'Referer': f'https://leetcode.com/problems/{title_slug}/',
        'Cookie': f'csrftoken={csrf_token}; LEETCODE_SESSION={leetcode_session}',
        'X-Csrftoken': csrf_token,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    }

    graphql_query = {
        "query": "query getQuestionContent($titleSlug: String!) { question(titleSlug: $titleSlug) { content } }",
        "variables": {"titleSlug": title_slug}
    }

    response = requests.post(url, json=graphql_query, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = data.get('data', {}).get('question', {}).get('content', '')

        clean_content = re.sub('<[^<]+?>', '', unescape(content)).replace('\n', ' ')
        return clean_content
    else:
        return "Failed to fetch the content. Status code: " + str(response.status_code)

csrf_token = "your_csrftoken_here"
leetcode_session = "your_leetcode_session_token_here"
title_slug = "two-sum"

content = fetch_leetcode_question_content(csrf_token, leetcode_session, title_slug)
print(content)
