from openai import OpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

def run_gpt_query(system, user_query, search_db, config_data):
    try:
        docs = search_db.similarity_search(user_query, int(config_data['similar_results']))  # Number of similar embedding results
    except Exception as err:
        return None, f"Не получилось построить эмбеддинг для запроса: {err}"

    message_content = '\n\n'.join([doc.page_content for doc in docs])
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f'Ответь на вопрос пользователя, используя информацию из документа ниже.\nДокумент: <doc>{message_content}</doc>. Не упоминай документ с информацией, указанный выше.\nЗапрос пользователя: {user_query}'}
    ]

    client = OpenAI(base_url="https://api.vsegpt.ru/v1")

    try:
        completion = client.chat.completions.create(
            model=config_data['model_LLM'],
            messages=messages,
            temperature=float(config_data['temperature'])
        )
        answer = completion.choices[0].message.content
        return message_content, answer
    except Exception as err:
        return message_content, f'ОШИБКА: Не удалось получить ответ от LLM: {err}'

def get_db(config_data):
    embedding_model = OpenAIEmbeddings(
        model=config_data['model_emb'],
        openai_api_base="https://api.vsegpt.ru/v1/",
        openai_api_key=config_data['vsegpt_API_key']
    )
    db = FAISS.load_local("docs_db_index", embedding_model)
    return db
