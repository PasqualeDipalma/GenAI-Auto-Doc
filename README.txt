ISTRUZIONI PER L'USO:

1) Creare un file .env, all'interno di ./GenAI-Auto-Doc, in cui dovrà essere salvato il token per utilizzare le API di GitHub, le chiavi per utilizzare le API di gemini e le API del provider OpenRouter.ai (https://openrouter.ai/settings/keys) nel seguente modo:
 	- API_KEY_Gemini = ""
 	- API_KEY = ""
 	- github_token = ""

2) Avviare il server per poter utilizzare le API:
 	-eseguire il file application.py e andare all'indirizzo che apparirà nel terminale

3) Verifica dello stato del server:
 	- è possibile verificare che il server sia online eseguendo la seguente richiesta direttamente nel browser: http://127.0.0.1:5002/genAI/

4) Generazione di una documentazione relativa ad un progetto salvato in locale o tramite link al repository di GitHub:
    
	*Se il progetto è salvato in locale:
        - eseguire una richiesta POST, tramite script, con url = "http://127.0.0.1:5002/genAI/doc_generation_local"
        - la richiesta dovrà avere:
            - headers = {"Content-Type": "application/json; charset=utf-8"}
            - il body dovrà contenere, obbligatoriamente, i path ASSOLUTI della cartella in cui è contenuto il progetto da documentare ed
               della cartella in cui verrà salvata la documentazione generata.
    
	*Se si vuole utilizzare un link al repository su GitHub:
        - eseguire una richiesta POST, tramite script, con url = "http://127.0.0.1:5002/genAI/doc_generation_github"
        - la richiesta dovrà avere:
            - headers = {"Content-Type": "application/json; charset=utf-8"}
            - il body dovrà contenere il link al repository e il path ASSOLUTO della cartella in cui verrà salvata la documentazione generata

Esempio script per la generazione di una documentazione con progetto salvato in locale (non modificare i nomi delle variabili presenti nel body):

	import requests

	url = "http://127.0.0.1:5002/genAI/doc_generation_local"

	data = {
        	"project_path": "",
        	"result_path": ""
        	}

	headers = {"Content-Type": "application/json; charset=utf-8"}

	response = requests.request("POST", url, headers=headers,json = data)

	print(response)


Esempio script per la generazione di una documentazione tramite link repository GitHub (non modificare i nomi delle variabili presenti nel body):

    import requests

    url = "http://127.0.0.1:5002/genAI/doc_generation_github"

    data = {
            "project_path": "https://github.com/DivergerThinking/pycodedoc",  #IL LINK DEVE ESSERE IN QUESTO FORMATO
            "result_path": ""
            }

    headers = {"Content-Type": "application/json; charset=utf-8"}

    response = requests.request("POST", url, headers=headers,json = data)
    
    print(response)


5) È possibile scegliere tra 3 diversi modelli per generare la documentazione. Il modello di default è Gemini 1.5 8b Flash 0827.
   Per cambiare il modello utilizzato sarà necessario andare nel file config.py e modificare la variabile default_model con:
   - gemini-pro: per utilizzare Gemini 1.5 Pro 0827
   - llama: per utilizzare Llama 3.1 405b-Instruct
   - gemini-flash: per utilizzare Gemini 1.5 8b Flash 0827 (modello di default)

   È consigliato utilizzare i primi due modelli solo nel caso il progetto contenga pochi file (<= 10) ed utilizzare
   il terzo modello nel caso il progetto abbia molti file (>= 10), questo a causa dei limiti di richieste delle API.
   Per informazioni sui limiti controllare i seguenti siti:
    - Gemini Pro e Flash: https://ai.google.dev/pricing#1_5flash
    - Llama 3.1 405b: https://openrouter.ai/docs/limits

6) È possibile utilizzare un modello in locale (quindi il modello verrà scaricato) modificando nel file config.yaml il valore della variabile model_type:
    - model_type: "local" -> per utilizzare un modello installato sulla propria macchina
    - model_type: "API" -> per utilizzare uno dei tre modelli disponibili tramite API
   
   Per specificare quale modello si vuole utilizzare sarà necessario modificare, in ./app/__init__.py, il valore della variabile model_id, per esempio:
    - model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
   
   Per poter utilizzare il modello sarà necessario inserire il token di Hugging Face nel file .env nel seguente modo:
    - hf_token = ""

7) (SOLO CON MODELLO LOCALE)
   È possibile far valutare ad un modello la documentazione generata effettuando una richiesta, tramite API, di tipo POST, come spiegato nel punto 4, con url = "http://127.0.0.1:5002/genAI/doc_generation_bench". Nel body, project_path dovrà contenere il path assoluto della documentazione da valutare.

Esempio script per la valutazione di una documentazione tramite modello locale:

	import requests

	url = "http://127.0.0.1:5002/genAI/doc_generation_bench"

	data = {
        	"project_path": "C:/User/Desktop/doc_gen.md",
        	"result_path": "C:/User/Desktop/result_folder"
        	}

	headers = {"Content-Type": "application/json; charset=utf-8"}

	response = requests.request("POST", url, headers=headers,json = data)

	print(response)