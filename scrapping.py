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
    # Look for the start of the Python class definition
    start_idx = content.find("class Solution:")
    if start_idx == -1:
        return None  # If the start isn't found, return None

    # Find the end of the code block, marked by triple backticks
    end_idx = content.find("```", start_idx)
    if end_idx != -1:
        # Extract the code block, excluding the closing backticks
        code_block = content[start_idx:end_idx]
    else:
        # If closing backticks are not found, extract everything from the start
        code_block = content[start_idx:]

    return code_block.strip()



def fetch_problems_title_slugs(csrf_token, leetcode_session, difficulty, limit=5, skip=400):
    """
    Fetches the titleSlugs of free hard problems from LeetCode.

    Args:
    csrf_token (str): CSRF token for authentication.
    leetcode_session (str): LeetCode session token for authentication.
    limit (int): Number of problems to fetch in one request.
    skip (int): Number of problems to skip.

    Returns:
    list: A list of titleSlugs for free hard problems.
    """

    url = "https://leetcode.com/graphql/"
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(categorySlug: $categorySlug, limit: $limit, skip: $skip, filters: $filters) {
            total: totalNum
            questions: data {
                titleSlug
                isPaidOnly
                difficulty
            }
        }
    }
    """
    
    variables = {
        "categorySlug": "",
        "skip": skip,
        "limit": limit,
        "filters": {
            "difficulty": difficulty
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"csrftoken={csrf_token}; LEETCODE_SESSION={leetcode_session}"
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        problems = data['data']['problemsetQuestionList']['questions']
        return [problem['titleSlug'] for problem in problems if not problem['isPaidOnly']]
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

# -------------- DATA FOR gpt-3.5-turbo-1106 --------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <csrf_token> <leetcode_session> <title_slug>")
    else:
        csrf_token = sys.argv[1]
        leetcode_session = sys.argv[2]
        
        title_slugs_hard = fetch_problems_title_slugs(csrf_token, leetcode_session, "HARD",120, 430)
        title_slugs_medium = fetch_problems_title_slugs(csrf_token, leetcode_session, "MEDIUM", 110, 1100)

        title_slugs = title_slugs_hard + title_slugs_medium
        
        with open("Data/dataGPT.jsonl", 'w') as file:
            for title_slug in title_slugs:
                question_content = clean_leetcode_content(fetch_leetcode_question_content(csrf_token, leetcode_session, title_slug))
                
                solution_id = fetch_python_solution_id(csrf_token, leetcode_session, title_slug)
                solution_content = fetch_solution_content(csrf_token, leetcode_session, solution_id)
                python_code = extract_python_code(solution_content)
                
                if python_code:
                    fine_tune_data = {
                        "messages": [
                            {"role": "user", "content": question_content},
                            {"role": "assistant", "content": python_code}
                        ]
                    }
                    
                    file.write(json.dumps(fine_tune_data) + '\n')


# -------------- DATA FOR DAVINCI-002 --------------
# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py <csrf_token> <leetcode_session> <title_slug>")
#     else:
#         csrf_token = sys.argv[1]
#         leetcode_session = sys.argv[2]
        
#         title_slugs = fetch_hard_problems_title_slugs(csrf_token, leetcode_session, 70, 430)
        
#         with open("Data/data.jsonl", 'w') as file:
#             for title_slug in title_slugs:
#                 question_content = clean_leetcode_content(fetch_leetcode_question_content(csrf_token, leetcode_session, title_slug))
                
#                 solution_id = fetch_python_solution_id(csrf_token, leetcode_session, title_slug)
#                 solution_content = fetch_solution_content(csrf_token, leetcode_session, solution_id)
#                 python_code = extract_python_code(solution_content)
                
#                 if python_code:
#                     fine_tune_data = {
#                         "prompt": "Write an optimized Python function to solve the following problem: " + question_content,
#                         "completion": python_code
#                     }
                    
#                     file.write(json.dumps(fine_tune_data) + '\n')

# Usage :
# python3 scrapping.py your_csrf_token your_leetcode_session_token 
