import json

with open("data.jsonl", 'r') as file:
    total_prompt_chars, total_completion_chars = 0, 0
    for line in file:
        data = json.loads(line)
        total_prompt_chars += len(data['prompt']) if data['prompt'] else 0
        total_completion_chars += len(data['completion']) if data['completion'] else 0
        
    print(f"Total characters in prompts: {total_prompt_chars}")
    print(f"Total characters in completions: {total_completion_chars}")
    print(f"Total : {total_prompt_chars + total_completion_chars}")

    print(f"Estimated cost : {((total_prompt_chars + total_completion_chars)/4000)* 0.0060 }")