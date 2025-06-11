import os  # importa módulo para variáveis de ambiente
import scrapy
from scrapy.http import FormRequest
from dotenv import load_dotenv

# Carrega .env (ENEM_LOGIN, ENEM_PASSWORD, ENEM_TARGET_REGISTRY, ENEM_YEAR)
load_dotenv()

class EnemSpider(scrapy.Spider):
    name = 'enem'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'ROBOTSTXT_OBEY': False,
    }

    def start_requests(self):
        # 1) Autenticação no sistema
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
        # 2) Submissão do formulário de login
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
        # 3) Verifica sucesso de login e inicia consulta direta
        if b'inicial' not in response.body:
            self.logger.error('Falha na autenticação')
            return
        self.logger.info('Autenticado com sucesso!')
        # Parâmetros de consulta
        registry = os.getenv('ENEM_TARGET_REGISTRY', '151000163729')
        year = os.getenv('ENEM_YEAR', '2015')
        consulta_path = f'/EnemSolicitacao/solicitacao/resultado{year}/numeroInscricao/solicitacaoPelaInternet.seam'
        consulta_url = response.urljoin(consulta_path)
        yield scrapy.Request(
            consulta_url,
            callback=self.parse_consulta,
            meta={'value': registry, 'year': year},
            dont_filter=True
        )

    def parse_consulta(self, response):
        # 4) Preenche o número de inscrição e envia pesquisa
        registry = response.meta['value']
        formdata = {
            'numerosInscricaoDecorate:numerosInscricaoInput': registry,
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
        # 5) Clica em "Salvar" para gerar solicitação
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
        # 6) Acessa página de acompanhamento após salvar
        acompanhar_url = response.urljoin(
            '/EnemSolicitacao/solicitacao/acompanharSolicitacao.seam'
        )
        yield scrapy.Request(
            acompanhar_url,
            callback=self.parse_table,
            meta=response.meta,
            dont_filter=True
        )

    def parse_table(self, response):
        # 7) Na tabela, busca a solicitação fechada e extrai link de Download
        rows = response.xpath('//table[@id="listaSolicitacaoAtendidas"]//tr[position()>1]')
        target = response.meta['value']
        download_rel = None
        for row in rows:
            num = row.xpath('normalize-space(.//td[2]/text())').get()
            status = row.xpath('normalize-space(.//td[4]/text())').get()
            if num == target and 'Fechado' in status:
                download_rel = row.xpath('.//a[contains(text(),"Download")]/@href').get()
                if download_rel:
                    break
        if not download_rel:
            self.logger.error(f"Link de Download não encontrado para {target}")
            return
        download_url = response.urljoin(download_rel)
        self.logger.info(f"Baixando arquivo via {download_url}")
        yield scrapy.Request(
            download_url,
            callback=self.save_file,
            meta=response.meta,
            dont_filter=True
        )

    def save_file(self, response):
        # 8) Salva o arquivo localmente (pode ser .txt ou .csv)
        kind = 'registry'
        value = response.meta['value']
        year = response.meta['year']
        ext = os.path.splitext(response.url)[1] or '.txt'
        filename = f"resultado_{kind}_{value}_{year}{ext}"
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.logger.info(f"Arquivo salvo em {filename}")