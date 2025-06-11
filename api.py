from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor
from enem_solicitacao_py.spiders.enem_spider import EnemSpider

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
runner = CrawlerRunner(get_project_settings())

app = FastAPI()

class ConsultaRequest(BaseModel):
    login: str
    password: str
    registry: str | None = None
    year: str | None = None

@app.post("/consulta")
async def consulta(req: ConsultaRequest):
    os.environ['ENEM_LOGIN'] = req.login
    os.environ['ENEM_PASSWORD'] = req.password
    if req.registry:
        os.environ['ENEM_TARGET_REGISTRY'] = req.registry
    if req.year:
        os.environ['ENEM_YEAR'] = req.year

    spider = EnemSpider()
    try:
        await runner.crawl(spider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not spider.result_content:
        raise HTTPException(status_code=500, detail="Nenhum conteudo gerado")

    return {"resultado": spider.result_content}
