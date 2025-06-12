from fastapi import FastAPI, HTTPException, Response
from dotenv import load_dotenv
import subprocess
import sys
import os

load_dotenv()

app = FastAPI()

@app.get('/consulta')
def consulta(registry: str, year: str):
    """Run the spider for the given registry and year and return the file content."""
    cmd = [
        sys.executable,
        '-m',
        'scrapy',
        'crawl',
        'enem',
        '-a', f'registry={registry}',
        '-a', f'year={year}',
    ]
    subprocess.run(cmd, check=False)

    for ext in ('.txt', '.csv'):
        filename = f'resultado_registry_{registry}_{year}{ext}'
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                content = f.read()
            media_type = 'text/plain'
            if ext == '.csv':
                media_type = 'text/csv'
            return Response(content=content, media_type=media_type)

    raise HTTPException(status_code=404, detail='Nenhum conteudo gerado')