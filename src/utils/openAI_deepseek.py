import requests
from openai import OpenAI

def deepseek(key, question, abstract):

    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key,
    )    
        
    response = client.chat.completions.create(
    model="deepseek/deepseek-r1:free",
    messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f'{question} {abstract}'},
        ],
    stream=False
    )

    if response and response.choices:
        print("Query successful")
        return f"`{response.choices[0].message.content}`"
    else:
        return "Error in query: No response received."
