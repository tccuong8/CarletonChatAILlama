import chromadb
import os
import csv
# from openai.embeddings_utils import get_embedding
from chromadb.utils import embedding_functions
from datetime import datetime
from openai import OpenAI
import decouple

def merge_dicts(dict1, dict2):
    """Merge two dictionaries into one."""
    merged_dict = dict1.copy()  # Make a copy of the first dictionary
    merged_dict.update(dict2)   # Update the copy with the second dictionary
    return merged_dict

try: # For ai_chat_bot.py access
  with open("semantic_search\\api_key.env", "r") as file:
      api_key=file.read()
except: 
  with open("api_key.env", "r") as file:
      api_key=file.read()
openai_client = OpenAI(api_key=api_key)
chroma_client = chromadb.PersistentClient(path="../embeddings")
embedding_model = "text-embedding-ada-002"

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key= api_key,
                model_name="text-embedding-ada-002"
            )

# collection = chroma_client.get_or_create_collection(name="tdx")
collection = chroma_client.delete_collection(name="tdx")
collection = chroma_client.get_or_create_collection(name="tdx")


with open("web-scraping\\article_text_no_newline.csv", "r", encoding='utf-8', errors='ignore') as f:
    next(f)
    reader = csv.reader(f)
    articles = list(reader)
    article_title_and_link = [{"title": article[0], "link": article[1]} for article in articles]
    # article_name_and_link = [merge_dicts(article_name[i],article_link[i]) for i in range(len(article_name))]
    # article_name_and_link = [{article_name[i]["title"]: article_link[i]["link"]} for i in range(len(article_name))]
    article_content = [article[2] for article in articles]
    article_ids = [f"{i}" for i in range (1,len(articles)+1)]
    # print(article_names)
    # articles_texts = [article[3] for article in articles]
    # articles_embeddings = [article[4] for article in articles]
    # for i in range(len(articles_embeddings)):
    #     embedding = articles_embeddings[i]
    #     embedding = embedding.replace("[", "")
    #     embedding = embedding.replace("]", "")
    #     embedding = embedding.split(",")
    #     embedding = [float(e) for e in embedding]
    #     articles_embeddings[i] = embedding

    # articles_metadata = [{"title": article[0], "date": getTimestamp(article[1]), "link": article[2]} for article in articles]
    # articles_ids = ["article" + str(i) for i in range(len(articles))]
    collection.add(
        # embeddings=articles_embeddings,
        documents=article_content,
        metadatas=article_title_and_link, # type: ignore
        ids=article_ids
    )
    
def query(gpt_message):
    results = collection.query(
        query_texts=[gpt_message],
        n_results=10
    )
    print(results)
    return results

# def getTimestamp(time_str):
#     #Time string format is month name day, year
#     return datetime.strptime(time_str, '%B %d, %Y').timestamp()