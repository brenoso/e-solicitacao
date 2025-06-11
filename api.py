from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from scrapy.crawler import CrawlerProcess
from enem_solicitacao_py.spiders.enem_spider import EnemSpider

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

    process = CrawlerProcess()
    spider = EnemSpider()
    try:
        process.crawl(spider)
        process.start()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not spider.result_content:
        raise HTTPException(status_code=500, detail="Nenhum conteúdo gerado")

    return {"resultado": spider.result_content}
