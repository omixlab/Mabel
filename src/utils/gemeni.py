import requests

def gemeni(key, question, text):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}

    data = {"contents": [{"parts": [{"text": f"{question} {text}"}]}]}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Query successful")
        res = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"`{res}`"
    else:
        return ("Error in query. Code status:", response.status_code)
