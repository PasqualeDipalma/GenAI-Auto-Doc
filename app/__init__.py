import os

from dotenv import load_dotenv
from fastapi import FastAPI
from config import Settings
import transformers
import torch

#Solo se si vuole utilizzare un modello in locale andiamo a caricare il modello
if Settings.get_model_type() == "local":

    load_dotenv()
    hf_token = os.getenv("hf_token")

    model_id = "Qwen/Qwen2.5-7B-Instruct"

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
        token = hf_token
    )

from app.views import router

app = FastAPI()

app.include_router(router.router)