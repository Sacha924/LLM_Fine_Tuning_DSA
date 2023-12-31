import json
import re
import sys
from html import unescape

import requests


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



def fetch_python_solution_id(csrf_token, leetcode_session, title_slug):
    """
    Fetch the ID of the first Python solution for a given LeetCode problem.
    """
    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'Referer': f'https://leetcode.com/problems/{title_slug}/',
        'Cookie': f'csrftoken={csrf_token}; LEETCODE_SESSION={leetcode_session}',
        'X-Csrftoken': csrf_token
    }
    query = {
        "query": """
        query questionSolutions($questionSlug: String!, $skip: Int!, $first: Int!, $orderBy: TopicSortingOption, $languageTags: [String!]) {
            questionSolutions(
                filters: {
                    questionSlug: $questionSlug,
                    skip: $skip,
                    first: $first,
                    orderBy: $orderBy,
                    languageTags: $languageTags
                }
            ) {
                solutions {
                    id
                    solutionTags {
                        slug
                    }
                }
            }
        }
        """,
        "variables": {
            "questionSlug": title_slug,
            "skip": 0,
            "first": 20,
            "orderBy": "most_votes",
            "languageTags": ["python3"]
        }
    }
    
    response = requests.post(url, json=query, headers=headers)
    if response.status_code == 200:
        solutions = response.json()['data']['questionSolutions']['solutions']
        for solution in solutions:
            if 'python3' in [tag['slug'] for tag in solution['solutionTags']]:
                return solution['id']
    return None


def fetch_solution_content(csrf_token, leetcode_session, solution_id):
    """
    Fetch the content of a solution by its ID.
    """
    url = 'https://leetcode.com/graphql'
    headers = {
        'Content-Type': 'application/json',
        'Referer': f'https://leetcode.com/problems/two-sum/solutions/{solution_id}/',
        'Cookie': f'csrftoken={csrf_token}; LEETCODE_SESSION={leetcode_session}',
        'X-Csrftoken': csrf_token
    }
    query = {
        "query": """
        query topic($topicId: Int!) {
            topic(id: $topicId) {
                post {
                    content
                }
            }
        }
        """,
        "variables": {
            "topicId": solution_id
        }
    }
    
    response = requests.post(url, json=query, headers=headers)
    if response.status_code == 200:
        content = response.json()['data']['topic']['post']['content']
        return content
    return None


def extract_python_code(content):
    """
    Extract Python code from the solution content.
    """
    python_code_match = re.search(r'```Python3\s*\[\]\s*([\s\S]*?)\s*```', content)
    if python_code_match:
        return python_code_match.group(1).strip()
    return None



if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <csrf_token> <leetcode_session> <title_slug>")
    else:
        csrf_token = sys.argv[1]
        leetcode_session = sys.argv[2]
        title_slugs = sys.argv[3].split(",")

        with open("data.jsonl", 'w') as file:
            for title_slug in title_slugs:
                question_content = clean_leetcode_content(fetch_leetcode_question_content(csrf_token, leetcode_session, title_slug))
                
                solution_id = fetch_python_solution_id(csrf_token, leetcode_session, title_slug)
                
                solution_content = fetch_solution_content(csrf_token, leetcode_session, solution_id)
                python_code = extract_python_code(solution_content)
                
                fine_tune_data = {
                    "prompt": question_content,
                    "completion": python_code
                }
                
                file.write(json.dumps(fine_tune_data) + '\n')

# Usage :
# python3 scrapping.py your_csrf_token your_leetcode_session_token title_slug_of_the_problem
