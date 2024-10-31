from openai import OpenAI
import os

from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings


# place your VseGPT key here
# os.environ["OPENAI_API_KEY"] = "sk-or-vv-abaef3de33810419220b9aab0053d4dc5801f6ee7547b50a7069722ebac88cbc"


def run_gpt_query(system, user_query, search_db, config_data):

    try:
        docs = search_db.similarity_search(user_query, int(config_data['similar_results'])) # число результатов схожих по эмбеддингу
    except Exception as err:
        print("Не получилось построить эмбеддинг для запроса")
        print(err)
        return err

    message_content = '\n\n'.join([doc.page_content for i, doc in enumerate(docs)])
    print('Используем следующую найденную информацию: ')
    print(message_content)
    print("----------------------------------")

    messages = [
      {"role": "system", "content": system},
      {"role": "user", "content": f'Ответь на вопрос пользователя, используя информацию из документа ниже.\n Документ: <doc>{message_content}</doc>. Не упоминай документ с информацией, указанный выше.\n Запрос пользователя: {user_query}'}]

    client = OpenAI(
        base_url="https://api.vsegpt.ru/v1",
    )
    
    try:
        completion = client.chat.completions.create(model=config_data['model_LLM'], messages=messages, temperature= float(config_data['temperature']))
        answer = completion.choices[0].message.content
        return message_content, answer
    except Exception as err:
        print('ОШИБКА: Не удалось получить ответ от LLM')
        print(err)
        return err


def get_db(config_data):
    embedding_model = OpenAIEmbeddings( model=config_data['model_emb'], 
                                        openai_api_base = "https://api.vsegpt.ru/v1/",
                                        openai_api_key = config_data['vsegpt_API_key'])
                                        
    db = FAISS.load_local("docs_db_index", embedding_model)
    return db
    