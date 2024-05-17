import os
import requests
from openai import OpenAI
import json

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NUMBERS_API_URL = "http://numbersapi.com/"


openai = OpenAI(
  api_key=OPENAI_API_KEY
)

def build_messages(user_query, number=None, fact_type=None):
  messages = [
    {
      "role": "system",
      "content": "Tell the user to provide a number if they don't provide one. They should also specify if they want a trivia fact or a a math fact."
    }
  ]

  if number and fact_type:
    messages.append({
      "role": "system",
      "content": f"The user has previously asked for a {fact_type} fact about {number}."
    })

  messages.append({
    "role": "user",
    "content": user_query
  })

  return messages

def build_params(user_query, number=None, fact_type=None):
  
  params = {
    "model": "gpt-4-turbo",
    "messages": build_messages(user_query, number, fact_type),
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_fact_from_numbers_api",
                "description": "Get a fun fact about a number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number": {
                            "type": "integer",
                            "description": "The number to get a fun fact about"
                        },
                        "fact_type": {
                            "type": "string",
                            "description": "The type of fact to get about the number, trivia or math"
                        }
                    },
                    "required": ["number", "fact_type"]
                }
            }
        },
    ]
  }

  return params



def get_number_fact(number, fact_type="trivia"):
  if fact_type not in ["trivia", "math"]:
    return "Invalid fact type. Please provide either 'trivia' or 'math'."
  elif fact_type == "math":
    response = requests.get(f"{NUMBERS_API_URL}{number}/math")
  else:
    response = requests.get(f"{NUMBERS_API_URL}{number}/trivia")

  return response.text

def return_message_from_system(message):
  return message

def main(prompt=None, query=None, number=None, fact_type=None):
  if query:
    user_query = query
  else:
    if prompt:
      user_query = input(f"{prompt}: ")
    else:
      user_query = input("Enter a number and a fact type (trivia or math): ")

  params = build_params(user_query, number, fact_type)

  response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=params["messages"],
    tools=params["tools"],
  )


  if response.choices[0].message.tool_calls:
    if response.choices[0].message.tool_calls[0].function.name == "get_fact_from_numbers_api":
      args = response.choices[0].message.tool_calls[0].function.arguments
      number = json.loads(args)["number"]
      fact_type = json.loads(args)["fact_type"]
      fact = get_number_fact(number, fact_type)
      print(fact)
      main(prompt="what else would you like to know?", number=number, fact_type=fact_type)
  else:
    system_message = return_message_from_system(response.choices[0].message.content)
    user_input = input(f"{system_message}: ")
    main(query=user_input)

if __name__ == "__main__":
  main()