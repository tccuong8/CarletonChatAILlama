"""
git pull
git add ...
git commit -m "<message>"
git push origin <branch name>
git fetch
	+ When other people delete branches, and you want for the same branch to also be deleted on your side.
 
SOURCE: https://platform.openai.com/docs/api-reference/introduction?lang=python
"""


import openai, os, tiktoken
from openai import OpenAI

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-0613":  # note: future models may deviate from this
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
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


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



# def old_code():
#   # my_assistant = client.beta.assistants.create(
#   #     instructions=gpt_instructions,
#   #     name="TDX assistant",
#   #     tools=[
#   #         {"type": "code_interpreter"}, # Commented out to avoid accidental charges ($0.03 per session)
#   #         {"type": "retrieval"}
#   #         ],
#   #     model=gpt_model,
#   # )

#   # # Use a relative or absolute path
#   # file_path = "D:\VS Code\Python\Projects\Git\Carleton ChatAI\Carleton-AI-Chat\web-scraping\\article_text_no_newline.xlsx"

#   # print(os.path.exists(file_path))
#   # # Check if the file exists
#   # if os.path.exists(file_path):
#   #     client.files.create(
#   #         file=open(file_path, "rb"),
#   #         purpose="assistants"
#   #     )
#   #     if debug_mode: print("File located:", file_path)
#   # else:
#   #     if debug_mode: print("File not found:", file_path)
#   #     quit()

#   # DIRECTLY ADDING FILES. NOT NEEDED, ALREADY DID SO ON THE API ON WEB BROWSER
#   # client.files.create(
#   #   file=open("D:\VS Code\Python\Projects\Git\Carleton ChatAI\Carleton-AI-Chat\web-scraping\\article_text_no_newline.xlsx", "rb"),
#   #   purpose="assistants" 
#   # )
#   # client.files.create(
#   #   file=open("Carleton-AI-Chat/web-scraping/articles.csv", "rb"),
#   #   purpose="assistants" 
#   # )
#   # client.files.create(
#   #   file=open("Carleton-AI-Chat/web-scraping/main_categories.csv", "rb"),
#   #   purpose="assistants" 
#   # )
#   # client.files.create(
#   #   file=open("Carleton-AI-Chat/web-scraping/popular_tags.csv", "rb"),
#   #   purpose="assistants" 
#   # )
#   # client.files.create(
#   #   file=open("Carleton-AI-Chat/web-scraping/sub_categories.csv", "rb"),
#   #   purpose="assistants" 
#   # )
  
#   # thread_messages = client.beta.threads.messages.list(ids["thread"])
#   # if debug_mode: 
#   #   print("Thread messages:", thread_messages.data)
#   #   print()
  
#   """Caching responses
#   # Later, retrieve the same response using its ID
#   cached_response = get_chat_completion(completion_id=new_response.id)
#   print("\nCached Response:")
#   print(cached_response)

#   if cached_response.choices:
#       # Assuming you want the first choice's message
#       response_message = cached_response.choices[0].message.content
#       print(response_message)
#   else:
#       print("No response received.")"""
      
#   # Run the message once. Result (response included)
#   """
#   D:\VS Code\Python\Projects\Git\Carleton ChatAI\Carleton-AI-Chat\semantic-search>python main.py
#   Assistant(id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', created_at=1702503144, description=None, file_ids=['file-HYnTIkjbJYqKzCS6RYPf0kJD', 'file-G4NlBi7IeFdp1qYV9fpOu0hy', 'file-jPJPAsBEOW1t59fYiS3wBKve', 'file-l5xefGTETTbM3yLc9scCDiGq'], instructions='TDX assistant will only answer questions using the new data we have provided under the knowledge section. It will never use training data from OpenAI. If there are any confusions, TDX assistant will ask the user for more clarifying questions instead of crashing.\n\nIn article_text.csv, texts are in HTML format. You will modify the text files so that there are changed from HTML format to plain text format. You will use these plain texts to answer user questions.', metadata={}, model='gpt-3.5-turbo-1106', name='TDX assistant', object='assistant', tools=[ToolCodeInterpreter(type='code_interpreter'), ToolRetrieval(type='retrieval')])

#   Thread(id='thread_DZCqbmdlOSvo2IZLtMYMHaUc', created_at=1702503263, metadata={}, object='thread')

#   ThreadMessage(id='msg_jowRdIYlCnIKQO783x4zq6aG', assistant_id=None, content=[MessageContentText(text=Text(annotations=[], value=''), type='text')], created_at=1702503351, file_ids=[], metadata={}, object='thread.message', role='user', run_id=None, thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc')

#   Run(id='run_5TafLs45ecJRlRx9I3wVEXCA', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', cancelled_at=None, completed_at=1702503425, created_at=1702503424, expires_at=None, failed_at=None, file_ids=[], instructions='TDX assistant will only answer questions using the new data we have provided under the knowledge section. It will never use training data from OpenAI. If there are any confusions, TDX assistant will ask the user for more clarifying questions instead of crashing.\n\nIn article_text.csv, texts are in HTML format. You will modify the text files so that there are changed from HTML format to plain text format. You will use these plain texts to answer user questions.', last_error=None, metadata={}, model='gpt-3.5-turbo-1106', object='thread.run', required_action=None, started_at=1702503425, status='expired', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc', tools=[])


#   New Response:
#   ChatCompletion(id='chatcmpl-8Y2c6NEVrCmYdHBlha8EzFGmpILPj', choices=[Choice(finish_reason='stop', index=0, message=ChatCompletionMessage(content='Hello! How can I assist you today?', role='assistant', function_call=None, tool_calls=None), logprobs=None)], created=1703123890, model='gpt-3.5-turbo-1106', object='chat.completion', system_fingerprint='fp_772e8125bb', usage=CompletionUsage(completion_tokens=9, prompt_tokens=111, total_tokens=120))

#   Next Response:
#   ChatCompletion(id='chatcmpl-8Y2c74rQI8IyDFxydCjK9HAxc7loF', choices=[Choice(finish_reason='stop', index=0, message=ChatCompletionMessage(content="Yes, I'm perfectly fine, thank you for asking! How can I assist you today?", role='assistant', function_call=None, tool_calls=None), logprobs=None)], created=1703123891, model='gpt-3.5-turbo-1106', object='chat.completion', system_fingerprint='fp_772e8125bb', usage=CompletionUsage(completion_tokens=19, prompt_tokens=109, total_tokens=128))

#     """

#   for i in range (3):
#     new_prompt = input("User Input: ")
#     all_messages.append({"role": "user", "content": new_prompt}) #Add user prompt 
#     # Call the API for a new completion
#     response = client.chat.completions.create(
#       model=gpt_model,
#       messages=all_messages,
#       # file_ids=ids["files"] # NEED TO GET THIS WORKING (It's working, I hope)
#     )
#     # Cache the new response with its ID
#     ids["chat_completions"][response.id] = response

    
#     # Store the new message in all_messages
#     message = response.choices[0].message.content 
#     all_messages.append({"role": "assistant", "content": message})
    
#     print("Assisstant Ouput: " + message + "\n")
    
#     if debug_mode:
#       print("Chat Completions:")
#       print(ids["chat_completions"])
#       print()
      
#     if debug_mode:
#       print("All messages:")
#       for thing in all_messages:
#         print(thing)
#       print()

#     run_steps = client.beta.threads.runs.steps.list(
#         thread_id=ids["thread"],
#         run_id=ids["run"]
#     )
#     if debug_mode: 
#       print("Run steps:", run_steps)
#       print()
  
  
#   """[
#   ThreadMessage(
#     id='msg_1CftpQfcU0WTjm9qcNEkGLVR', 
#     assistant_id=None, 
#     content=[
#       MessageContentText(
#         text=Text(annotations=[], value=''), 
#         type='text'
#       )
#     ], 
#     created_at=1703123891, 
#     file_ids=[], 
#     metadata={}, 
#     object='thread.message', 
#     role='user', 
#     run_id=None, 
#     thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'
#   ), 
#   ThreadMessage(
#     id='msg_R2Vm94TuT403vSQY4Uaizi25', 
#     assistant_id=None, 
#     content=[
#       MessageContentText(
#         text=Text(annotations=[], value=''), 
#         type='text'
#       )
#     ], 
#     created_at=1703123890, 
#     file_ids=[], 
#     metadata={}, 
#     object='thread.message', 
#     role='user', 
#     run_id=None, 
#     thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'
#   ), 
#   ThreadMessage(id='msg_eKsqLfkoSFdwyWvKlWdpF1ml', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='It seems that there was an issue with accessing the content of the uploaded files. Could you please re-upload the files so that I can assist you effectively?'), type='text')], created_at=1702939163, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_bizEhc8GvbG5a43VncXuTIxn', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_lIhCw03ueG4vytnbJpS3jDR3', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='It seems that there was an issue with accessing the content of the uploaded files. Could you please re-upload the files so that I can assist you effectively?'), type='text')], created_at=1702915233, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_wamQdTyO7QGGPPiQqUpMVQLO', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_wEz25ktalklUhO7IAQ6WpIPc', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='What do you need help with?'), type='text')], created_at=1702913626, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_hmvm32LqNV8zjU9h1hPwpwaO', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_ITqiprrnZU21P8Ag40Fc8VC3', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='What do you need help with?'), type='text')], created_at=1702666512, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_tqToySseWon2pF2BJvrdn8tV', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_sBRBiBKMI7Zr6yOJBmRSNqfR', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='What do you need help with?'), type='text')], created_at=1702666469, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_6lUmP6ws4DC55yu92P16ffcr', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_TOHSKWzHKBeE4uYgTJAgqrCu', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='What do you need help with?'), type='text')], created_at=1702661010, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_GpjTp3PMbhrUJHmTbW40R3h0', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_I3f1cdYhNsIkiG5zIQd5Cn5k', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value="I'm sorry, but I can't assist with that."), type='text')], created_at=1702581512, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_I11ubAM1BKXK5corU2xe01K3', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_AEGzONFinMuOGK5VXFKTeemL', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value="I'm sorry, but I can't assist with that."), type='text')], created_at=1702570868, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_T52dGvGo5LcAnyLSOuKKH7dG', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_SMAxzlxBeCxiIdjdb1JPL4Fh', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value="I'm sorry, but I can't assist with that."), type='text')], created_at=1702505751, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_Gw8nw46pNFDfmZbJteyeCRYz', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_62sgf6Obk0bsSmdgNl3VYyLx', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value="I'm sorry, but I can't assist with that."), type='text')], created_at=1702505670, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_qPMd3fUVCU0AlJTSVjVauCEk', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_DJQ9n0NcwQmkmmuQSmZF8Sl8', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='Hello! How can I assist you today?'), type='text')], created_at=1702505639, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_QZTPCTIdS8BxwNwr7gU9ucSN', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_qmE3WxxwUcFpbLuySQXbrM2G', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='Hello! How can I assist you today? If you have any questions or need help with something, feel free to ask.'), type='text')], created_at=1702505611, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_2L7eCq7bWC949kPJwgJ88tzn', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_Pn3Bs1xe5sTleaAoHvsDv11J', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='Hello! How can I assist you today? If you have any questions or need help with something, feel free to ask.'), type='text')], created_at=1702505578, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_Awo3QwnsBJ1IwotcvKp3tkrO', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_N4HBDtYm2gYAHccE5cNwUk6r', assistant_id='asst_dxT9wjMwRt6XPzeo3tu7kTtT', content=[MessageContentText(text=Text(annotations=[], value='Hello! How can I assist you today?'), type='text')], created_at=1702503425, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_5TafLs45ecJRlRx9I3wVEXCA', thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc'), ThreadMessage(id='msg_jowRdIYlCnIKQO783x4zq6aG', assistant_id=None, content=[MessageContentText(text=Text(annotations=[], value=''), type='text')], created_at=1702503351, file_ids=[], metadata={}, object='thread.message', role='user', run_id=None, thread_id='thread_DZCqbmdlOSvo2IZLtMYMHaUc')]
#   """
  
  
  