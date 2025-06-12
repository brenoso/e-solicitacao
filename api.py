from fastapi import FastAPI, HTTPException, Response
from dotenv import load_dotenv
import subprocess
import sys
import os

load_dotenv()

app = FastAPI()

@app.get('/consulta')
def consulta(year: str, registry: str | None = None, cpf: str | None = None):
    """Run the spider for the given registry or CPF and year and return the file content."""
    if not registry and not cpf:
        raise HTTPException(status_code=400, detail='registry ou cpf é obrigatório')

    cmd = [
        sys.executable,
        '-m',
        'scrapy',
        'crawl',
        'enem',
    ]
    if registry:
        cmd += ['-a', f'registry={registry}']
    if cpf:
        cmd += ['-a', f'cpf={cpf}']
    cmd += ['-a', f'year={year}']
    subprocess.run(cmd, check=False)

    base = None
    if registry:
        base = f'resultado_registry_{registry}_{year}'
    elif cpf:
        base = f'resultado_cpf_{cpf}_{year}'

    if base:
        for ext in ('.txt', '.csv'):
            filename = f'{base}{ext}'
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    content = f.read()
                media_type = 'text/plain'
                if ext == '.csv':
                    media_type = 'text/csv'
                return Response(content=content, media_type=media_type)

    raise HTTPException(status_code=404, detail='Nenhum conteudo gerado')
