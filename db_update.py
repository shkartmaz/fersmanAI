import os
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tika import parser

def list_dif(first, second):
    return [item for item in first if item not in second]

def create_search_db(file_text, knowledge_base_link, chunk_size=1024, chunk_overlap=200, update=False, emb_model="text-embedding-3-large", api_key="0"):
    splitter = RecursiveCharacterTextSplitter(['\n\n', '\n', ' '], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    source_chunks = []

    # Splitting text into chunks
    for chunkID, chunk in enumerate(splitter.split_text(file_text)):
        source_chunks.append(Document(page_content=chunk, metadata={'source': knowledge_base_link, 'chunkID': chunkID}))

    if source_chunks:
        embedding_model = OpenAIEmbeddings(model=emb_model, openai_api_base="https://api.vsegpt.ru/v1/", openai_api_key=api_key)
        try:
            db = FAISS.from_documents(source_chunks, embedding_model)
        except Exception as err:
            return f"ОШИБКА: Не удалось построить векторную базу данных. {err}"
        else:
            if not update:
                db.save_local("docs_db_index")
                return "Docs.db search index created!"
            else:
                db_old = FAISS.load_local("docs_db_index", embedding_model)
                db_old.merge_from(db)
                db_old.save_local("docs_db_index")
                return "Docs.db search index updated!"

def get_file_list():
    db_hash_old = []
    try:
        with open("db_hash.txt") as f_in:
            db_hash_old = [line.split() for line in f_in]
    except FileNotFoundError:
        print("Предыдущих версий не найдено")
    
    default_folder = "data/"
    file_paths = os.listdir(default_folder)
    file_paths = [default_folder + path for path in file_paths]
    db_hash_new = [[path, str(os.path.getmtime(path))] for path in file_paths]
    
    with open("db_hash.txt", "w", encoding="utf-8") as f_out:
        for item in db_hash_new:
            f_out.write(f"{item[0]}\t{item[1]}\n")
        
    diff = list_dif(db_hash_new, db_hash_old)
    if not diff:
        return None
    else:
        return [x[0] for x in diff]

def get_data(file_paths):
    data = ""
    file_count = 0
    for path in file_paths:
        try:
            parsed_file = parser.from_file(path)
            data += parsed_file['content']
            file_count += 1
        except Exception as err:
            print(f"ОШИБКА: Проблемы с файлом {path}. {err}")
    
    with open("data.txt", "w", encoding="utf-8") as f_out:
        f_out.write(data)

    return data

def update_vector_database(config_data):
    file_paths = get_file_list()
    if file_paths is not None:
        data = get_data(file_paths)
        knowledge_base_link = "shkartmaz_knowledge_base"
        return create_search_db(data, knowledge_base_link, 
                                 chunk_size=int(config_data['chunk_size']),
                                 chunk_overlap=int(config_data['chunk_overlap']),
                                 emb_model=config_data['model_emb'],
                                 api_key=config_data['vsegpt_API_key'])
    else:
        return "Векторная база данных актуальна. Изменений не обнаружено."
