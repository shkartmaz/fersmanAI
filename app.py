from flask import Flask, render_template, request, redirect, url_for, flash
import configparser
import os
from db_update import *
from db_search import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    config_values = {
        'vsegpt_API_key': config.get('General', 'vsegpt_API_key'),
        'chunk_size': config.get('Embedding', 'chunk_size'),
        'chunk_overlap': config.get('Embedding', 'chunk_overlap'),
        'similar_results': config.get('Embedding', 'similar_results'),
        'model_emb': config.get('Embedding', 'model'),
        'model_LLM': config.get('LLM', 'model'),
        'temperature': config.get('LLM', 'temperature')
    }
    return config_values

def update_config(config_data):
    config = configparser.ConfigParser()
    config['General'] = {'vsegpt_API_key': config_data['vsegpt_API_key']}
    config['Embedding'] = {
        'chunk_size': config_data['chunk_size'],
        'chunk_overlap': config_data['chunk_overlap'],
        'similar_results': config_data['similar_results'],
        'model': config_data['model_emb']
    }
    config['LLM'] = {
        'model': config_data['model_LLM'],
        'temperature': config_data['temperature']
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

@app.route('/')
def index():
    config_data = get_config()
    return render_template('index.html', config=config_data)

@app.route('/send_prompt', methods=['POST'])
def send_prompt():
    prompt = request.form['prompt']
    config_data = get_config()
    response_content = ''

    if prompt:
        # LLM call
        message_content, response = run_gpt_query(
            "Ты - помощник, помогающий отвечать на вопросы",
            prompt,
            get_db(config_data),
            config_data
        )
        response_content = {
            'message_content': message_content,
            'response': response,
            'prompt': prompt
        }
    else:
        flash("Введите непустой запрос.")

    return render_template('index.html', config=config_data, response_content=response_content)

@app.route('/update_database')
def update_database():
    update_vector_database(get_config())
    flash("База данных обновлена")
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    config_data = get_config()
    if request.method == 'POST':
        new_config_data = {
            'vsegpt_API_key': request.form['vsegpt_API_key'],
            'chunk_size': request.form['chunk_size'],
            'chunk_overlap': request.form['chunk_overlap'],
            'similar_results': request.form['similar_results'],
            'model_emb': request.form['model_emb'],
            'model_LLM': request.form['model_LLM'],
            'temperature': request.form['temperature']
        }
        update_config(new_config_data)
        flash("Настройки изменены")
        return redirect(url_for('settings'))
    
    return render_template('settings.html', config=config_data)

@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == "__main__":
    app.run(debug=True)
