import os
import requests
import json
import time
import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from sympy.physics.units import temperature

from config import *


load_dotenv()

GEMINI_API_KEY = os.getenv("API_KEY_Gemini")
genai.configure(api_key = GEMINI_API_KEY)

PROVIDER_API_KEY = os.getenv("API_KEY")

# Genera documentazione per un singolo file
def gemini_gen_desc_file(file_to_doc, system_prompt):

    # Create the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 1,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name = "gemini-1.5-flash-8b-exp-0827",
        generation_config = generation_config,
        system_instruction = system_prompt
    )

    chat_session = model.start_chat()

    response = chat_session.send_message("Write a detailed documentation about this file: \n"
                               f"{file_to_doc}")

    return response.text



# Genera documentazione per un progetto con molti file.
# Vengono passati un file per richiesta per generare le singole documentazioni, queste vengono poi date all'LLM
# che genererà la documentazione dell'intero progetto
def gemini_flash_gen_doc(model, files_to_read, project_structure, github_project):
    try:
        #------------------------------- GENERAZIONE DESCRIZIONE SINGOLO FILE ---------------------------
        all_files_desc = []

        # Carica diversi prompt a seconda del numero di file da leggere
        if len(files_to_read) > 10:
            system_prompt_files = load_PROMPTS['MANY_FILES_SYSTEM_PROMPT']
            system_prompt_project = load_PROMPTS['BIG_PROJECT_SYSTEM_PROMPT']
        else:
            system_prompt_files = load_PROMPTS['FEW_FILES_SYSTEM_PROMPT']
            system_prompt_project = load_PROMPTS['SMALL_PROJECT_SYSTEM_PROMPT']

        # Se non è un progetto di github è necessario leggere i contenuti di tutti i file
        print(f"Inizio: {datetime.datetime.now()}")
        if not github_project:
            for files in files_to_read:
                with open(files, "r", encoding="utf8") as f:
                    single_file_content = f.read()
                f.close()

                #Genera descrizione di un singolo file
                file_desc = gemini_gen_desc_file(single_file_content, system_prompt_files)
                time.sleep(model.sleep_time) # Sleep per non superare il limite di richieste al minuto

                all_files_desc.append(file_desc)

        else: # Se è un progetto di github i contenuti dei file di script sono già stati letti
            for file in files_to_read:
                file_desc = gemini_gen_desc_file(file, system_prompt_files)

                all_files_desc.append(file_desc)


        # ------------------------------------------------------------------------------------------------

        # ------------------------------- GENERAZIONE DESCRIZIONE INTERO PROGETO -------------------------

        generation_config = {
            "temperature": model.model_parameters['temperature'],
            "top_p": model.model_parameters['top_p'],
            "top_k": model.model_parameters['top_k'],
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name=model.model_name,
            generation_config = generation_config,
            system_instruction = system_prompt_project
        )

        chat_session = model.start_chat()

        response = chat_session.send_message("Write a description about this project and write what it does and how. \n"
                                             f"Project files descriptions: {all_files_desc} \n"
                                             "Before you start writing the documentation analize how the project is structured\n"
                                             f"Project structure: {project_structure}")

        print(f"Fine: {datetime.datetime.now()}")
        return response.text
    except Exception as e:
        print(e)


#Genera documentazione per un progetto che ha pochi file che vengono passati tutti in una sola richiesta
# Utilizza Gemini 1.5 Pro 002 per generare la documentazione
def gemini_pro_gen_doc(model, files_to_read, project_structure):

    system_prompt = load_PROMPTS['SMALL_PROJECT_SYSTEM_PROMPT']
    generation_config = {
        "temperature": model.model_parameters['temperature'],
        "top_p": model.model_parameters['top_p'],
        "top_k": model.model_parameters['top_k'],
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name= model.model_name,
        generation_config = generation_config,
        system_instruction = system_prompt
    )

    chat_session = model.start_chat()

    response = chat_session.send_message("Write a description about this project and write what it does and how. \n"
                                         f"Project file: {files_to_read} \n"
                                         "Before you start writing the documentation analize how the project is structured\n"
                                         f"Project structure: {project_structure}")

    return response.text

#Genera documentazione per un progetto che ha pochi file che vengono passati tutti in una sola richiesta
# Utilizza Llama 3.1 405b Instruct per generare la documentazione
def llama_gen_doc(model, files_to_read, project_structure):

    system_prompt = load_PROMPTS['SMALL_PROJECT_SYSTEM_PROMPT']
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {PROVIDER_API_KEY}",
        },
        data=json.dumps({
            "model": model.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": "Write a description about this project and write what it does and how. \n"
                               f"Project file: {files_to_read} \n"
                               "Before you start writing the documentation analyze how the project is structured\n"
                               f"Project structure: {project_structure}"
                }
            ],
            "top_p": model.model_parameters['top_p'],
            "temperature": model.model_parameters['temperature'],
            "frequency_penalty": model.model_parameters['frequency_penalty'],
            "presence_penalty": model.model_parameters['presence_penalty'],
            "repetition_penalty": model.model_parameters['repetition_penalty'],
            "top_k": model.model_parameters['top_k']

        })
    )

    chat = response.json()

    return chat['choices'][0]['message']['content']

def local_model_gen_desc(pipeline, file_to_doc, system_prompt):
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a detailed documentation about this file: \n {file_to_doc}"},
        ]

        outputs = pipeline(
            messages,
            max_new_tokens = 30000,
            temperature = 0.9
        )
        return outputs[0]["generated_text"][-1]["content"]

    except Exception as e:
        print(e)

def local_model_gen_doc(pipeline, files_to_read, project_structure, github_project):
    all_files_desc = []

    # Carica diversi prompt a seconda del numero di file da leggere
    if len(files_to_read) > 10:
        system_prompt_files = load_PROMPTS['MANY_FILES_SYSTEM_PROMPT']
        system_prompt_project = load_PROMPTS['BIG_PROJECT_SYSTEM_PROMPT']
    else:
        system_prompt_files = load_PROMPTS['FEW_FILES_SYSTEM_PROMPT']
        system_prompt_project = load_PROMPTS['SMALL_PROJECT_SYSTEM_PROMPT']

    try:
        # Se non è un progetto di github è necessario leggere i contenuti di tutti i file
        print(f"Inizio: {datetime.datetime.now()}")
        if not github_project:
            for single_file_content in files_to_read:
                # Genera descrizione di un singolo file
                file_desc = local_model_gen_desc(pipeline, single_file_content, system_prompt_files)
                time.sleep(Settings.get_sleep_time())  # Sleep per non superare il limite di richieste al minuto

                all_files_desc.append(file_desc)

        else:  # Se è un progetto di github i contenuti dei file di script sono già stati letti
            for file in files_to_read:
                file_desc = local_model_gen_desc(pipeline, file, system_prompt_files)

                all_files_desc.append(file_desc)

            # ------------------------------------------------------------------------------------------------

            # ------------------------------- GENERAZIONE DESCRIZIONE INTERO PROGETO -------------------------

        messages = [
            {"role": "system", "content": system_prompt_project},
            {"role": "user", "content": "Write a description about this project and write what it does and how. \n"
                                                 f"Project files descriptions: {all_files_desc} \n"
                                                 "Before you start writing the documentation analyze how the project is structured\n"
                                                 f"Project structure: {project_structure}"},
        ]

        outputs = pipeline(
            messages,
            max_new_tokens = 20000,
            temperature = 0.9
        )
        return outputs[0]["generated_text"][-1]["content"]

    except Exception as e:
        print(e)

# Genera una valutazione della documentazione secondo dei parametri inseriti nel prompt
# Utilizza un modello installato sulla propria macchina
def doc_benchmark(pipeline, doc_path):
    system_prompt = load_PROMPTS['BENCHMARK_PROMPT']

    with open(doc_path, "r") as f:
        doc = f.read()
    f.close()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "I will give to you a project documentation, please evaluate it \n"
                                    f"Project Documentation: \n {doc}"},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens = 23000,
        temperature = 0.9
    )
    return outputs[0]["generated_text"][-1]["content"]



