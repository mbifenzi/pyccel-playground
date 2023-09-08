import json
from fastapi import FastAPI, Form
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


import compiler

class Item(BaseModel):
    text: str
    language: str

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://pyccel-playground.vercel.app",
    "https://pyccel-playground.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
async def root():
    return {"message": "Hello World, check /docs please for how to use the API"}

@app.get("/pyccel-version")
async def pyccel_version():
    version = compiler.Pyccel_version()
    if not version:
        return {"PyccelBackend:": "Backend Couldn't get the version"}
    return version


async def dompiler(item_text, item_language):
  # This function is asynchronous
  response =  compiler.Backend_compiler(item_text, item_language)
  return response

async def Executor(item_text, item_language):
  # This function is asynchronous
  response =  compiler.Backend_Executer(item_text, item_language)
  return response


@app.post("/submit-python")
async def submit_python(item : Item):
    """Submit a code and return translation."""

    if not item.text:
        raise HTTPException(
            status_code=400,
            detail="Please provide some text.",
        )
    if item.language not in ["c", "fortran", "python"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid language. Supported languages are: c, fortran, python.",
        )

    response = await dompiler(item.text, item.language)
    if not response:
        return {"PyccelBackend:": "Backend Couldn't Compile the code"}
    return response


@app.post("/execute-python")
async def execute_python(item : Item):
    """Submit a code and return translation."""

    if not item.text:
        raise HTTPException(
            status_code=400,
            detail="Please provide some text.",
        )
    if item.language not in ["c", "fortran", "python"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid language. Supported languages are: c, fortran, python.",
        )

    #response = await compiler.Backend_compiler(item.text, item.language)
    response = await Executor(item.text, item.language)
    if not response:
        return {"PyccelBackend:": "Backend Couldn't Compile the code"}
    return response
