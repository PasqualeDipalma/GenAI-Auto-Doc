import json

from fastapi import APIRouter, Response
from app.service.genDoc.project_doc import GenProjectDoc
from app.service.validator.request_validator import DocInputPaths

router = APIRouter(prefix="/genAI", tags=[""])

#Richiesta GET per controllare lo stato del server
@router.get('/')
async def statuscheck():
    return Response(json.dumps({'Status': 'Available'}),
                    status_code=200,
                    media_type='application/json')

#Richiesta POST per generare la documentazione di un progetto salvato in locale
@router.post('/doc_generation_local')
async def project_doc_generation_local(paths: DocInputPaths):
    """

    :param paths: DocInputPaths
            oggetto di tipo DocInputPaths per gestire gli input della richiesta e validarli
    :return: Response
            risposta alla richiesta, di tipo JSON
    """
    try:
        doc_gen = GenProjectDoc(paths.project_path, paths.result_path)

        project_structure, scripts_files_path = doc_gen.get_all_files_and_directories()

        doc = doc_gen.gen_doc(scripts_files_path, project_structure, False)

        if len(doc) != 0:
            doc_path = GenProjectDoc.write_doc(doc_gen, doc)
            response_service = dict(detail={'msg': f'documentation: {doc} ', 'doc_path': f'{doc_path}'})

            return Response(json.dumps(response_service), media_type='application/json')
        else:
            return Response(json.dumps(dict(detail={'msg': 'Errore nella generazione della documentazione'})),
                    status_code=500, media_type='application/json')

    except Exception as e:
        print(e)
        print("Non è stato possibile generare la documentazione")


#Richiesta POST per generare la documentazione di un progetto utilizzando un link al repository di GitHub
@router.post('/doc_generation_github')
async def project_doc_generation_github(paths: DocInputPaths):
    """

    :param paths: DocInputPaths
            oggetto di tipo DocInputPaths per gestire gli input della richiesta e validarli
    :return: Response
            risposta alla richiesta, di tipo JSON
    """
    try:
        project_structure, files_content = GenProjectDoc.read_all_github_files(paths.project_path)
    except Exception as e:
        print(e)
        print("Non è stato possibile leggere i file del progetto da GitHub! \n")
        return Response(json.dumps(dict(detail={'msg': 'Non è stato possibile leggere i file del progetto da GitHub'})),
                 status_code=500, media_type='application/json')

    try:
        doc_gen = GenProjectDoc(paths.project_path, paths.result_path)

        doc = doc_gen.gen_doc(files_content, project_structure, True)

        if len(doc) != 0:
            doc_path = GenProjectDoc.write_doc(doc_gen, doc)
            response_service = dict(detail={'msg': f'documentation: {doc} ', 'doc_path': f'{doc_path}'})

            return Response(json.dumps(response_service), media_type='application/json')
        else:
            return Response(json.dumps(dict(detail={'msg': 'Errore nella generazione della documentazione'})),
                    status_code=500, media_type='application/json')

    except Exception as e:
        print(e)
        print("Non è stato possibile generare la documentazione")

@router.post('/doc_generation_bench')
async def doc_benchmark(paths: DocInputPaths):
    try:
        llm_eval = GenProjectDoc.doc_evaluation(paths.project_path)

        if len(llm_eval) != 0:
            GenProjectDoc.write_benchmark(llm_eval, paths.result_path)
            response_service = dict(detail={'msg': f'llm_eval: {llm_eval} ', 'doc_path': f'{paths.result_path}'})
            return Response(json.dumps(response_service), media_type='application/json')
        else:
            return Response(json.dumps(dict(detail={'msg': 'Errore nella generazione della valutazione della documentazione'})),
                            status_code=500, media_type='application/json')


    except Exception as e:
        print(e)
        print("Non è stato possibile valutare la documentazione \n")





