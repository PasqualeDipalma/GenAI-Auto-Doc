from app.service.genDoc.llm_models import *
from github import Github

#Estensioni dei file da leggere
extension = (".py", ".html", ".css", ".js", ".php",".java", ".c", ".cpp",".xml")

class GenProjectDoc:
    #Carica info su:
    # - modello utilizzato
    # - paramentri del modello
    # - path della cartella del progetto
    # - path della cartella in cui salvare le doc generate
    # - sleep_time per non eccedere le richieste per minuto
    def __init__(self, project_path, output_path):
        self.model_name = Settings.get_llm_model()
        self.model_parameters = Settings.get_llm_parameters()
        self.project_path = project_path
        self.output_path = output_path
        self.sleep_time = Settings.get_sleep_time()
        self.model_type = Settings.get_model_type()

    # Restituisce la struttara della cartella del progetto da documentare e i path di tutti i file di codice da analizzare
    def get_all_files_and_directories(self):
        data = {}
        files_path = []
        for (current_folder, folders_in_current_folder, files_in_current_folder) in os.walk(self.project_path):
            data[current_folder] = {}
            data[current_folder]['folder-list'] = folders_in_current_folder
            data[current_folder]['file-list'] = files_in_current_folder

            for filename in files_in_current_folder:
                if filename.endswith(extension):
                    files_path.append(os.path.join(current_folder, filename))

        return data, files_path

    # Salva documentazione generata in un file di tipo markdown
    # Riceve in input:
    # - doc : documentazione da salvare
    @staticmethod
    def write_doc(llm, doc):

        if llm.model_name == "gemini-1.5-pro-exp-0827":
            model = "Gemini 1.5 Pro"
        elif llm.model_name == "meta-llama/llama-3.1-405b-instruct:free":
            model = "Llama 3.1 405b"
        elif llm.model_name == "gemini-1.5-flash-8b-exp-0827":
            model = "Gemini 1.5 Flash 8b"
        else:
            model = "LLM"

        doc_title = f"GenDoc - {model}.md"

        doc_path = os.path.join(llm.output_path, doc_title)

        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc)

        return doc_path

    # Legge tutti i file di codice passati in input
    # Restituisce una lista con tutti i contenuti di tutti i file letti
    @staticmethod
    def read_all_files(scripts_files_path):
        all_file_content = []

        for files in scripts_files_path:
            with open(files, "r", encoding="utf8") as f:
                single_file_content = f.read()

            all_file_content.append(single_file_content)

        return all_file_content

    # Utilizza le API di GitHub per leggere tutti i file presenti all'interno di un repository
    # Riceve in input il link del repository
    # Restituisce due liste:
    #  - project_structure = contiene i paths di tutti i file presenti nel progetto
    #  - all_files_content = contiene i contenuti di tutti i file di script del progetto
    @staticmethod
    def read_all_github_files(github_path):
        load_dotenv()
        github_token = os.getenv('github_token')
        g = Github(github_token)

        repo_path = github_path.replace("https://github.com/", "")

        project_structure = []
        all_files_content = []
        try:
            repo = g.get_repo(repo_path)
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    project_structure.append(file_content.path)

                if file_content.path.endswith(extension):
                    script_content = repo.get_contents(file_content.path)
                    decoded = script_content.decoded_content

                    all_files_content.append(decoded)

            return project_structure, all_files_content

        except Exception as e:
            print(e)



    #Genera le documentazioni dei files passati in input tenendo conto della struttura del progetto
    def gen_doc(self, files_to_read, project_structure, github_project):
        if self.model_type == "API":
            if self.model_name == "gemini-1.5-pro-exp-0827":
                if not github_project:
                    files_to_read = GenProjectDoc.read_all_files(files_to_read)
                return gemini_pro_gen_doc(self, files_to_read, project_structure)

            elif self.model_name == "meta-llama/llama-3.1-405b-instruct:free":
                if not github_project:
                    files_to_read = GenProjectDoc.read_all_files(files_to_read)
                return llama_gen_doc(self, files_to_read, project_structure)

            elif self.model_name == "gemini-1.5-flash-8b-exp-0827":
                return gemini_flash_gen_doc(self, files_to_read, project_structure, github_project)

        else:
            from app import pipeline
            if not github_project:
                files_to_read = GenProjectDoc.read_all_files(files_to_read)

            return local_model_gen_doc(pipeline, files_to_read, project_structure, github_project)

    @staticmethod
    def write_benchmark(llm_eval, result_path):
        doc_path = os.path.join(result_path, "LLM-EVAL.md")

        with open(doc_path, "w") as f:
            f.write(llm_eval)
        f.close()

    @staticmethod
    def doc_evaluation(doc_path):
        from app import pipeline
        if Settings.get_model_type() == "local":
            llm_evaluation = doc_benchmark(pipeline, doc_path)

            return llm_evaluation
        else:
            raise Exception("E' necessario utilizzare un modello in locale per poter utilizare questa funzione")
