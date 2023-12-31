import re
from html import unescape

import requests
import sys


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

def clean_leetcode_content(content):
    """
    Clean the LeetCode content by removing extra spaces and the follow-up section.

    :param content: Raw content from LeetCode
    :return: Cleaned content
    """
    content = content.split("Follow-up:")[0]     # sometimes there is a "Follow-up" section in leetcode statement, i don't want it
    content = ' '.join(content.split())          # I get multiple spaces, so let's clean that

    return content


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <csrf_token> <leetcode_session> <title_slug>")
    else:
        csrf_token = sys.argv[1]
        leetcode_session = sys.argv[2]
        title_slug = sys.argv[3]

        content = clean_leetcode_content(fetch_leetcode_question_content(csrf_token, leetcode_session, title_slug))

        print(content)

# Usage :
# python3 scrapping.py your_csrf_token your_leetcode_session_token title_slug_of_the_problem
