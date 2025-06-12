import os  # importa módulo para variáveis de ambiente
import scrapy
from scrapy.http import FormRequest
from dotenv import load_dotenv
from datetime import datetime

# Carrega .env (ENEM_LOGIN, ENEM_PASSWORD, ENEM_TARGET_REGISTRY, ENEM_TARGET_CPF, ENEM_YEAR)
load_dotenv()

class EnemSpider(scrapy.Spider):
    name = 'enem'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'ROBOTSTXT_OBEY': False,
        'TWISTED_REACTOR': 'twisted.internet.selectreactor.SelectReactor',
    }

    def __init__(self, registry: str | None = None, cpf: str | None = None, year: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = registry
        self.cpf = cpf
        self.year = year
        self.result_content: bytes | None = None
        self.result_extension: str | None = None

    def start_requests(self):
        login = os.getenv('ENEM_LOGIN')
        password = os.getenv('ENEM_PASSWORD')
        if not login or not password:
            self.logger.error('Variáveis ENEM_LOGIN e ENEM_PASSWORD devem estar definidas.')
            return
        yield scrapy.Request(
            url='http://sistemasenem.inep.gov.br/EnemSolicitacao/login.seam',
            callback=self.parse_login,
            meta={'login': login, 'password': password},
            dont_filter=True
        )

    def parse_login(self, response):
        login = response.meta['login']
        password = response.meta['password']
        formdata = {
            'username': login,
            'password': password,
            'j_id19.x': '1',
            'j_id19.y': '1'
        }
        yield FormRequest.from_response(
            response,
            formid='formLogin',
            formdata=formdata,
            callback=self.after_login,
            dont_filter=True
        )

    def after_login(self, response):
        if b'inicial' not in response.body:
            self.logger.error('Falha na autenticação')
            return
        self.logger.info('Autenticado com sucesso!')
        registry = self.registry or os.getenv('ENEM_TARGET_REGISTRY')
        cpf = self.cpf or os.getenv('ENEM_TARGET_CPF')
        year = self.year or os.getenv('ENEM_YEAR', '2015')

        if registry:
            consulta_path = f'/EnemSolicitacao/solicitacao/resultado{year}/numeroInscricao/solicitacaoPelaInternet.seam'
            meta = {'value': registry, 'year': year, 'kind': 'registry'}
        elif cpf:
            consulta_path = f'/EnemSolicitacao/solicitacao/resultado{year}/cpf/solicitacaoPelaInternet.seam'
            meta = {'value': cpf, 'year': year, 'kind': 'cpf'}
        else:
            self.logger.error('Nenhum registry ou CPF informado')
            return

        consulta_url = response.urljoin(consulta_path)
        yield scrapy.Request(
            consulta_url,
            callback=self.parse_consulta,
            meta=meta,
            dont_filter=True
        )

    def parse_consulta(self, response):
        kind = response.meta['kind']
        value = response.meta['value']
        if kind == 'registry':
            formdata = {
                'numerosInscricaoDecorate:numerosInscricaoInput': value,
                'j_id131.x': '81',
                'j_id131.y': '23'
            }
        else:
            formdata = {
                'cpfDecorate:cpfInput': value,
                'j_id131.x': '81',
                'j_id131.y': '23'
            }
        yield FormRequest.from_response(
            response,
            formid='formularioForm',
            formdata=formdata,
            callback=self.parse_result_form,
            meta=response.meta,
            dont_filter=True
        )

    def parse_result_form(self, response):
        form = response.xpath('//form[@id="resultadoForm"]')
        if not form:
            self.logger.warning(f"Nenhum formulário de resultado para {response.meta['value']}")
            return
        yield FormRequest.from_response(
            response,
            formid='resultadoForm',
            formdata={'j_id191.x': '72', 'j_id191.y': '19'},
            callback=self.parse_acompanhar,
            meta=response.meta,
            dont_filter=True
        )

    def parse_acompanhar(self, response):
        acompanhar_url = response.urljoin(
@@ -116,33 +143,35 @@ class EnemSpider(scrapy.Spider):

        if not rows:
            self.logger.error('[PARSE_TABLE] Nenhuma linha de solicitação encontrada')
            return

        # Primeiro elemento da lista é a solicitação mais recente conforme ordem da página
        first = rows[0]
        sol_id_last = first.xpath('normalize-space(.//td[1]//text())').get(default='')
        link_last = first.xpath('.//td[last()]//a[contains(text(),"Download")]/@href').get()
        if not link_last:
            self.logger.error(f"[PARSE_TABLE] Link de download não encontrado para {sol_id_last}")
            return

        download_url = response.urljoin(link_last)
        self.logger.info(f"[PARSE_TABLE] Solicitação mais recente selecionada: id={sol_id_last}")
        self.logger.info(f"[PARSE_TABLE] Baixando arquivo: {download_url}")

        yield scrapy.Request(
            download_url,
            callback=self.save_file,
            meta=response.meta,
            dont_filter=True
        )

    def save_file(self, response):
        kind = response.meta.get('kind', 'registry')
        value = response.meta['value']
        year = response.meta['year']
        ext = os.path.splitext(response.url)[1] or '.txt'
        filename = f"resultado_{kind}_{value}_{year}{ext}"
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.result_content = response.body
        self.result_extension = ext
        self.logger.info(f"Arquivo salvo em {filename}")