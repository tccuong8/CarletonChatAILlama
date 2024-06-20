
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
import os, pgpt_python
# from pgpt_python.client import PrivateGPTApi

# def num_tokens_from_messages(messages, model="TheBloke/Llama-2-13B-chat-GGML"):
#   """Returns the number of tokens used by a list of messages."""
#   try:
#       encoding = tiktoken.encoding_for_model(model)
#   except KeyError:
#       encoding = tiktoken.get_encoding("cl100k_base")
#   if model == "":  # note: future models may deviate from this
#       num_tokens = 0
#       for message in messages:
#           num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
#           for key, value in message.items():
#               num_tokens += len(encoding.encode(value))
#               if key == "name":  # if there's a name, the role is omitted
#                   num_tokens += -1  # role is always required and always 1 token
#       num_tokens += 2  # every reply is primed with <im_start>assistant
#       return num_tokens
#   else:
#       raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
#   See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


try: # For ai_chat_bot.py access
  with open("semantic_search\\api_key.env", "r") as file:
      api_key=file.read()
except: 
  with open("api_key.env", "r") as file:
      api_key=file.read()

client = OpenAI(
    api_key=api_key
    # api_key=config("OPENAI_API_KEY") #Old code, in case new is buggy
)

debug_mode = False
gpt_model = "gpt-3.5-turbo-1106"

ids = {
	"assistant": "asst_dxT9wjMwRt6XPzeo3tu7kTtT",
	"thread": "thread_DZCqbmdlOSvo2IZLtMYMHaUc",
	"messages": [
    "msg_jowRdIYlCnIKQO783x4zq6aG"
  ],
	"run": "run_5TafLs45ecJRlRx9I3wVEXCA",
  "files": [
    "file-l5xefGTETTbM3yLc9scCDiGq", #main-categories
    "file-jPJPAsBEOW1t59fYiS3wBKve", #articles
    "file-HYnTIkjbJYqKzCS6RYPf0kJD", #sub-categories
    "file-G4NlBi7IeFdp1qYV9fpOu0hy", #Popular Tags
    "file-Aim7diitivcZ8jW0IazzobyP"  #article text no newline
  ],
  "chat_completions" : {
    
  }
}


gpt_instructions="""TDX assistant will only answer questions using the new data we have provided. It will never use training data from OpenAI or anything else that we didn't provide to it. If there are any confusions, TDX assistant will ask the user for more clarifying questions instead of crashing. TDX assistant will use these plain texts to answer user questions."""

all_messages=[{"role": "system", "content": gpt_instructions}]


for file_id in ids["files"]:
  assistant_file = client.beta.assistants.files.create(
    assistant_id=ids["assistant"],
    file_id=file_id
  )
  
  if debug_mode: 
    print(assistant_file)
    print()


assistant_files = client.beta.assistants.files.list(
  assistant_id=ids["assistant"]
)


my_assistant = client.beta.assistants.retrieve(ids["assistant"])


# my_thread = client.beta.threads.create() 
my_thread = client.beta.threads.retrieve(ids["thread"])


# message = client.beta.threads.messages.create(
#   ids["thread"],
#   role="user",
#   content="",
# )
message = client.beta.threads.messages.retrieve(
  message_id=ids["messages"][0],
  thread_id=ids["thread"],
)


# run = client.beta.threads.runs.create(
#   thread_id=ids["thread"],
#   assistant_id=ids["assistant"]
# )
run = client.beta.threads.runs.retrieve(
  thread_id=ids["thread"],
  run_id=ids["run"]
)


def chat(all_messages, new_prompt):
  all_messages.append({"role": "user", "content": new_prompt}) #Add user prompt 
  # Call the API for a new completion
  response = client.chat.completions.create(
    model=gpt_model,
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
  
  print("Files list:")
  print(assistant_files)
  print()
  
  print("My Assistant:")
  print(my_assistant)
  print()
  
  print("My Thread:")
  print(my_thread)
  print()
  
  print("Message:")
  print(message)
  print()
  
  print("Run:")
  print(run)
  print()
  
  print("Chat Completions:")
  print(ids["chat_completions"])
  print()

  print("All messages:")
  for thing in all_messages:
    print(thing)
  print()



"""ChatCompletion Object structure:
ChatCompletion(
  id='chatcmpl-8VlW430CEYaeFcA0q9Qgqblz3dQsL', 
  choices=[
    Choice(
      finish_reason='stop', 
      index=0, 
      message=ChatCompletionMessage(
        content="I'm here to help with your questions! What do you need assistance with today?", 
        role='assistant', 
        function_call=None, 
        tool_calls=None
      )
    )
  ], 
  created=1702581512, 
  model='gpt-3.5-turbo-1106', 
  object='chat.completion', 
  system_fingerprint='fp_f3efa6edfc', 
  usage=CompletionUsage(
    completion_tokens=17, 
    prompt_tokens=110, 
    total_tokens=127
  )
)"""

