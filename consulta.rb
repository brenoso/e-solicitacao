require 'dotenv/load'
require 'enem_solicitacao'

session = EnemSolicitacao::Session.new(
  ENV['ENEM_LOGIN'],
  ENV['ENEM_PASSWORD']
)

gateway = EnemSolicitacao::Gateway.new(session, 2015)

puts "Consultando número de inscrição #{ENV['ENEM_LOGIN']}..."
puts gateway.search_by_registry(ENV['ENEM_LOGIN'])
