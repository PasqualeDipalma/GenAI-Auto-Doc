import yaml

#Carica i paramentri presenti nel file di configurazione
load_config = yaml.safe_load(open('Resources/config.yaml', 'rb'))
load_PROMPTS = yaml.safe_load(open('Resources/PROMPTS.yaml', 'rb'))

#Modello da utilizzare,tre possibili scelte:
# - gemini-flash : Gemini 1.5 Flash 8b  (DA UTILIZZARE QUANDO SI HANNO > 10 FILES)
# - gemini-pro : Gemini 1.5 Pro 002  (DA UTILIZZARE SOLO QUANDO SI HANNO <= 10 FILES)
# - llama : Llama 3.1 405b Instruct  (DA UTILIZZARE SOLO QUANDO SI HANNO <= 10 FILES)
default_model = "gemini-flash"

model_engine = load_config[default_model]
model_type = load_config['model_type']

class Settings:

    #Restituisce il nome del modello che si sta utilizzando
    @staticmethod
    def get_llm_model():
        return model_engine['engine']

    #Restituisce i parametri del modello in uso
    @staticmethod
    def get_llm_parameters():
        return load_config[default_model]['parameters']

    #Restituisce i PROMPT da utilizzare nella generazione delle documentazioni
    @staticmethod
    def get_prompts():
        return load_PROMPTS

    #Restituisce il numero di secondi da aspettare prima di effettuare una nuova richiesta
    @staticmethod
    def get_sleep_time():
        return load_config['sleep_time']

    @staticmethod
    def get_model_type():
        return model_type
