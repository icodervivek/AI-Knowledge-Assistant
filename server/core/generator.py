import os
from groq import Groq

# import ollama

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# def generate_answer(prompt: str):
#     response = ollama.chat(
#         model="llama3.2:1b",
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
        
#     )
    
#     return response["message"]["content"]


def generate_answer(prompt: str):
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    )
    return response.choices[0].message.content