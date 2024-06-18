import openai
# from openai.error import InvalidRequestError
from openai import OpenAI
from decouple import config
from flask import Flask, request, send_from_directory, render_template, Response, abort, make_response, jsonify
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import func
from time import sleep
import dotenv
from os import environ
from datetime import datetime
# from eventlet import requests

with open("api_key.env", "r") as file:
    api_key=file.read()

client = OpenAI(
    api_key=api_key
    # api_key=config("OPENAI_API_KEY") #Old code, in case new is buggy
)

my_assistant = client.beta.assistants.create(
    instructions="""TDX assistant will only answer questions using the new data we have provided under the knowledge section. It will never use training data from OpenAI. If there are any confusions, TDX assistant will ask the user for more clarifying questions instead of crashing.

In article_text.csv, texts are in HTML format. You will modify the text files so that there are changed from HTML format to plain text format. You will use these plain texts to answer user questions.""",
    name="TDX assistant",
    tools=[
        # {"type": "code_interpreter"} # Commented out to avoid accidental charges ($0.03 per session)
        ],
    model="gpt-3.5-turbo",
)
print(my_assistant)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to search for the most used word in our database. Can you help me?"
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=my_assistant.id
)

run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)

messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

dotenv.load_dotenv()

app = Flask(__name__, template_folder=".")
CORS(app)

db = SQLAlchemy()
class ChatRecord(db.Model):
	__tablename__ = 'chattpirecords' 
	id = db.Column(db.Integer, primary_key=True)
	chat = db.Column(db.Text, nullable=False)
	datetime = db.Column(db.DateTime, nullable=False)

	def __repr__(self):
		return f"ChatRecord('{self.chat}', '{self.datetime}')"

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URI')
db.init_app(app)

def get_hypothetical_document(messages):
	try:
		messages.append({'role': 'user', 'content': "Ignore all of the past questions. Answer it purely from your own knowledge. Try to answer the question as if you were a human."})
		response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=False)
		print(response)
	except InvalidRequestError:
		if len(messages) > 3:
			messages.pop(1)
			messages.pop()
			response, messages = get_hypothetical_document(messages)
		else:
			raise Exception
	except Exception:
		raise Exception
	messages.pop()
	return response.choices[0].message.content, messages

def get_final_output(messages, sources, count):
	systemContent = "Use the following documents to answer the question:"
	for i in range(len(sources)):
		systemContent += "title: " + sources[i]['title'] + " text: " + sources[i]['text'] + "\n"
	messages.append({'role': 'user', 'content': systemContent})
	try:
		next = ''
		for resp in openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=True):
			r = resp.choices[0]
			if not 'content' in r['delta']:
				continue
			if r['finish_reason'] == 'stop':
				break
			next += r['delta']['content']
			if '\n' in next:
				emit("output", next)
				print(next)
				next = ''
		if next != '':
			emit("output", next)
			print(next)
	except InvalidRequestError as e:
		print(e)
		if count < 5 and len(messages) > 3:
			messages.pop(1)
			get_final_output(messages, sources, count + 1)
		else:
			raise Exception
	return response.choices[0].message.content

@app.route("/submitChat", methods=['POST'])
def submit_chat(data):
	data = request.get_json()
	chat = data['chat']
	try:
		#Get next id
		maxId = db.session.query(func.max(ChatRecord.id)).all()
		print(maxId)
		if maxId[0][0] == None:
			maxId = 1
		else:
			maxId = maxId[0][0]+1
		print(maxId)
		chatRecord = ChatRecord(id=maxId, chat=str(chat[-1]['text']), datetime=datetime.now())
		db.session.add(chatRecord)
		db.session.commit()
	except Exception as e:
		print(e)
	finally:
		emit("HyDE", 'Retrieving sources...')
		# #First we get the hypothetical document
		messages = [{'role': 'system', 'content': 'You are a helpful chatbot. You will answer questions to the best of your ability. If a list of sources are provided, you will answer the question with those sources and refer to them in the answer.'}]
		for i in range(len(chat)):
			messages.append({'role': chat[i]['user'], 'content': chat[i]['text']})
		# hyde = messages[-1]['content']
		try:
			hyde, messages = get_hypothetical_document(messages)
			#Then we get the related documents
			embed = requests.post('url/getEmbed', json={'prompt': hyde}).json()
			results = requests.post('url/getResults', json={'embed': embed, 'offset': 0, 'startDate': "2002-01-01T00:00:00.000Z", 'endDate': "2023-06-30T00:00:00.000Z"})
			sources = results.json()
			try:
				get_final_output(messages, sources, 0)
			except Exception as e:
				print(e)
				emit("error", "Error getting sources. Please rephrase your question and try again.")
		except Exception as e:
			#Return input too long error
			print(e)
			emit("Error", "Question is too long. Please try again with a shorter question.")

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a smart and charismatic college student assistant, patient and skilled in guiding users to web articles that they desire."},
    {"role": "user", "content": "What are the best articles to learn about how ChatGPT works?"}
  ]
)
print(completion.choices[0].message)