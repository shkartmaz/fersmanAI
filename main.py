import tkinter as tk
import sys
import configparser
from tkinter import simpledialog, messagebox, scrolledtext

from db_update import *
from db_search import *

def display_welcome_message(config_data):
    print("Добро пожаловать!")
    print("Если это первый запуск программы, нажмите 'Обновить базу данных'")
    
    # print("Текущие настройки программы:")
    # print(config_data)
    
    
def get_config():
     # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    vsegpt_API_key = config.get('General', 'vsegpt_API_key')
    chunk_size = config.get('Embedding', 'chunk_size')
    chunk_overlap = config.get('Embedding', 'chunk_overlap')
    similar_results = config.get('Embedding', 'similar_results')
    model_emb = config.get('Embedding', 'model')
    model_LLM = config.get('LLM', 'model')
    temperature = config.get('LLM', 'temperature')
    
    # Return a dictionary with the retrieved values
    config_values = {
        'vsegpt_API_key' : vsegpt_API_key,
        'chunk_size' : chunk_size,
        'chunk_overlap' : chunk_overlap,
        'similar_results' : similar_results,
        'model_emb' : model_emb,
        'model_LLM' : model_LLM,
        'temperature' : temperature
    }

    return config_values


def update_config(config_data):
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['General'] = {   'vsegpt_API_key'    : config_data['vsegpt_API_key']}
    config['Embedding'] = { 'chunk_size'        : config_data['chunk_size'],
                            'chunk_overlap'     : config_data['chunk_overlap'],
                            'similar_results'   : config_data['similar_results'],
                            'model'             : config_data['model_emb']}
    config['LLM'] = {       'model'             : config_data['model_LLM'],
                            'temperature'       : config_data['temperature']}
                            
    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

class RedirectText(object):
    def __init__(self, text_ctrl):
        self.output = text_ctrl
        
    def write(self, string):
        self.output.insert(tk.END, string)

class MainApp:
    def __init__(self, master):
    
        config_data = get_config()
        os.environ["OPENAI_API_KEY"] = config_data['vsegpt_API_key']
    
        self.master = master
        master.title("FersmanAI v0.1")
        

        # Dialog box to display prompts and responses
        self.dialog_box = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=120, height=25, state='disabled')
        self.dialog_box.pack(pady=10)
        # Redirect stdout to dialog_box
        redir = RedirectText(self.dialog_box)
        sys.stdout = redir
        
        self.dialog_box.config(state='normal')
        display_welcome_message(config_data)
        self.dialog_box.config(state='disabled')
        self.dialog_box.yview(tk.END)  # Scroll to the end

        self.prompt_label = tk.Label(master, text="Введите запрос:")
        self.prompt_label.pack(pady=5)

        self.prompt_entry = tk.Entry(master, width=60)
        self.prompt_entry.pack(pady=5)
        self.prompt_entry.bind('<Return>', self.send_prompt)  # Bind Enter key

        # Frame for buttons to arrange them inline
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.send_button = tk.Button(button_frame, text="Отправить (ENTER)", command=self.send_prompt)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = tk.Button(button_frame, text="Обновить базу данных", command=self.update_database)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.settings_button = tk.Button(button_frame, text="Настройки", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)
        
        self.help_button = tk.Button(button_frame, text="Помощь", command=self.open_help)
        self.help_button.pack(side=tk.LEFT, padx=5)

    def send_prompt(self, event=None):
        prompt = self.prompt_entry.get()
        config_data = get_config()
        if prompt:
                    
            # LLM call
            message_content, response = run_gpt_query("Ты - помощник, помогающий отвечать на вопросы",
                                        prompt,
                                        get_db(config_data),
                                        config_data)
            
            # Update dialog box with prompt and response
            self.dialog_box.config(state='normal')
            self.dialog_box.insert(tk.END, "\n\nИспользуем следующую найденную информацию:\n")
            self.dialog_box.insert(tk.END, message_content)
            self.dialog_box.insert(tk.END, f"\n\nYOU: {prompt}\n")
            self.dialog_box.insert(tk.END, f"LLM: {response}\n\n")
            self.dialog_box.config(state='disabled')
            self.dialog_box.yview(tk.END)  # Scroll to the end
            
            self.prompt_entry.delete(0, tk.END)  # Clear the entry
            
        else:
            messagebox.showwarning("Предупреждение", "Введите непустой запрос.")
            
    def update_database(self):
        self.dialog_box.config(state='normal')
        self.dialog_box.insert(tk.END, "Проверка наличия изменений в папке data...\n")
        update_vector_database(get_config())
        self.dialog_box.config(state='disabled')
        self.dialog_box.insert(tk.END, "База данных обновлена\n")
        self.dialog_box.yview(tk.END)  # Scroll to the end

    def open_settings(self):
        settings_window = SettingsWindow(self.master)
        
    def open_help(self):
        help_window = HelpWindow(self.master)


class SettingsWindow:
    def __init__(self, master):
        config_data = get_config()
    
        self.settings_window = tk.Toplevel(master)
        self.settings_window.title("Настройки")
        
        current_row = 0

        self.api_label = tk.Label(self.settings_window, text="vsegpt.ru API key")
        self.api_label.grid(row=current_row, column=0)

        self.api_entry = tk.Entry(self.settings_window, width=25)
        self.api_entry.insert(0, config_data['vsegpt_API_key'])
        self.api_entry.grid(row=current_row, column=1)
        current_row += 1
        
        self.chunksize_label = tk.Label(self.settings_window, text="Размер чанка")
        self.chunksize_label.grid(row=current_row, column=0)

        self.chunksize_entry = tk.Entry(self.settings_window, width=10)
        self.chunksize_entry.insert(0, config_data['chunk_size'])
        self.chunksize_entry.grid(row=current_row, column=1)
        current_row += 1
        
        self.chunkoverlap_label = tk.Label(self.settings_window, text="Перекрытие чанков")
        self.chunkoverlap_label.grid(row=current_row, column=0)

        self.chunkoverlap_entry = tk.Entry(self.settings_window, width=10)
        self.chunkoverlap_entry.insert(0, config_data['chunk_overlap'])
        self.chunkoverlap_entry.grid(row=current_row, column=1)
        current_row += 1
        
        self.chunknum_label = tk.Label(self.settings_window, text="Количество чанков при запросе")
        self.chunknum_label.grid(row=current_row, column=0)

        self.chunknum_entry = tk.Entry(self.settings_window, width=10)
        self.chunknum_entry.insert(0, config_data['similar_results'])
        self.chunknum_entry.grid(row=current_row, column=1)
        current_row += 1
        
        self.embedding_label = tk.Label(self.settings_window, text="Модель для эмбеддинга")
        self.embedding_label.grid(row=current_row, column=0)
        
        self.embedding_entry = tk.Entry(self.settings_window, width=25)
        self.embedding_entry.insert(0, config_data['model_emb'])
        self.embedding_entry.grid(row=current_row, column=1)
        current_row += 1
        
        self.LLM_label = tk.Label(self.settings_window, text="Языковая модель")
        self.LLM_label.grid(row=current_row, column=0)
        
        self.LLM_entry = tk.Entry(self.settings_window, width=25)
        self.LLM_entry.insert(0, config_data['model_LLM'])
        self.LLM_entry.grid(row=current_row, column=1)
        current_row += 1
        
        self.temperature_label = tk.Label(self.settings_window, text="Температура")
        self.temperature_label.grid(row=current_row, column=0)
        
        self.temperature_entry = tk.Entry(self.settings_window, width=10)
        self.temperature_entry.insert(0, config_data['temperature'])
        self.temperature_entry.grid(row=current_row, column=1)
        current_row += 1
        

        self.save_button = tk.Button(self.settings_window, text="Сохранить", command=self.save_settings)
        self.save_button.grid(row=current_row, columnspan=2)     
        

    def save_settings(self):
        config_data = {}
        config_data['vsegpt_API_key']   = self.api_entry.get()
        config_data['chunk_size']       = self.chunksize_entry.get()
        config_data['chunk_overlap']    = self.chunkoverlap_entry.get()
        config_data['similar_results']  = self.chunknum_entry.get()
        config_data['model_emb']        = self.embedding_entry.get()
        config_data['model_LLM']        = self.LLM_entry.get()
        config_data['temperature']      = self.temperature_entry.get()
        
        update_config(config_data)
        
        # Here you would save the parameters or apply them to the LLM call
        messagebox.showinfo("Настройки изменены")
       
        self.settings_window.destroy()
        
class HelpWindow:
    def __init__(self, master):
        
        self.help_window = tk.Toplevel(master)
        self.help_window.title("Помощь")
        
        self.help_box = scrolledtext.ScrolledText(self.help_window, wrap=tk.WORD, width=60, height=25, state='disabled')
        self.help_box.pack(pady=10)
        
        self.help_box.config(state='normal')
        self.help_box.insert(tk.END, "Эта программа отвечает на вопросы на основе содержания документации в папке data.\n\n")
        self.help_box.insert(tk.END, "Для этого она читает файлы (поддерживаются txt, rtf, doc, ppt,  xls, pdf, html и многое другое), делит их на чанки и векторизует эти чанки с помощью эмбеддинговой нейросети, формируя векторную базу данных.\n\n")
        self.help_box.insert(tk.END, "Запрос пользователя также векторизуется и сравнивается с базой данных. Несколько наиболее похожих чанков передается как контекст для LLM, которая с их помощью отвечает на исходный запрос.\n\n")
        self.help_box.insert(tk.END, "При первом запуске, или при изменении/ добавлении файлов в папке data во время работы программы, нажмите ОБНОВИТЬ БАЗУ ДАННЫХ\n\n")
        self.help_box.config(state='disabled')
        self.help_box.yview(tk.END)  # Scroll to the end

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
