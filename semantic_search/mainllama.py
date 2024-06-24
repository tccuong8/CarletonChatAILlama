
# This one is for the chat gpt version
# "https://learn.deeplearning.ai/courses/chatgpt-building-system/lesson/2/language-models%2C-the-chat-format-and-tokens"


# This is the thread about the conversation if we can implement llama instead of the chatgpt.

# "https://community.deeplearning.ai/t/chatbot-with-llama2/440420/2"
#

# This is for the  implementation of the llama instead of ChatGPT 3.5
# "https://vilsonrodrigues.medium.com/run-llama-2-models-in-a-colab-instance-using-ggml-and-ctransformers-41c1d6f0e6ad"

"""
git pull
git add ...
git commit -m "<message>"
git push origin <branch name>
git fetch
	+ When other people delete branches, and you want for the same branch to also be deleted on your side.
 
SOURCE: https://platform.openai.com/docs/api-reference/introduction?lang=python
"""

# import tiktoken
import os, sys
sys.path.insert(0, "c:/users/tranc2/appdata/local/programs/python/python312/lib/site-packages")
import pgpt_python, tiktoken # type: ignore
from pgpt_python.client import PrivateGPTApi # type: ignore

def num_tokens_from_messages(messages, model="TheBloke/Llama-2-13B-chat-GGML"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
#   See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


client = PrivateGPTApi(base_url="http://localhost:8001")

debug_mode = False

gpt_model = "gpt-3.5-turbo-1106" #replace this with the model we want to have.

gpt_instructions="""TDX assistant will only answer questions using the new data we have provided. It will never use training data from OpenAI or anything else that we didn't provide to it. If there are any confusions, TDX assistant will ask the user for more clarifying questions instead of crashing. TDX assistant will use these plain texts to answer user questions."""

all_messages=[{"role": "system", "content": gpt_instructions}]

print(client.health.health())


def chat(all_messages, new_prompt):
  all_messages.append({"role": "user", "content": new_prompt}) #Add user prompt 
  # Call the API for a new completion
  response = client.chat.completions.create(
    model= gpt_model,
    messages=all_messages,
  )
  # Cache the new response with its ID
  ids["chat_completions"][response.id] = response

  
  # Store the new message in all_messages
  message = response.choices[0].message.content 
  all_messages.append({"role": "assistant", "content": message})
  
  return all_messages, message

# Execution code, moved to a function call in ai_chat_web
def execute():
  global all_messages
  i=1
  new_prompt = ""
  while new_prompt != "Exit":
    new_prompt = input("User Input: ")
    all_messages, message = chat(all_messages, new_prompt)
    
    print("Assistant Output: " , message , "\n")
    print(f"Total tokens used: {num_tokens_from_messages(all_messages)}")
    print(f"Average tokens used: {num_tokens_from_messages(all_messages)/i}")
    print("Note: There may be some calculation errors due to there being a priming system message, and the unknown way the token counting funtion works.")
    print()
    i+=1
# execute()
  
if debug_mode:
  print("Client model:")
  print(client.models.list())
  print("Client model concluded")

  print("All messages:")
  for thing in all_messages:
    print(thing)
  print()


