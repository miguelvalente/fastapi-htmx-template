from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from jinja2_fragments.fastapi import Jinja2Blocks

templates = Jinja2Blocks("templates")
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def get_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
