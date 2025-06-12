from fastapi import FastAPI, HTTPException, Response
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from enem_solicitacao_py.spiders.enem_spider import EnemSpider
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get('/consulta')
def consulta(registry: str, year: str):
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(EnemSpider, registry=registry, year=year)
    process.start()
    spider = list(process.crawlers)[0].spider if process.crawlers else None

    content = getattr(spider, 'result_content', None)
    if content is None:
        raise HTTPException(status_code=404, detail='Nenhum conteudo gerado')

    media_type = 'text/plain'
    ext = getattr(spider, 'result_extension', '')
    if ext and ext.lower() == '.csv':
        media_type = 'text/csv'
    return Response(content=content, media_type=media_type)