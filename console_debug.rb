# console_debug.rb
require 'dotenv/load'
$LOAD_PATH.unshift File.expand_path('lib', __dir__)
require 'enem_solicitacao'

def salvar_html(nome, conteudo)
  path = "debug_#{nome}.html"
  File.write(path, conteudo)
  puts "📄 HTML salvo em #{path}"
end

def tentar_consulta_por_anos(input, tipo)
  (2010..2023).reverse_each do |ano|
    puts "\n🔄 Ano #{ano}..."
    begin
      session = EnemSolicitacao::Session.new(
        ENV['ENEM_LOGIN'],
        ENV['ENEM_PASSWORD']
      )
      gateway = EnemSolicitacao::Gateway.new(session, ano)

      resultado = tipo == :cpf ? gateway.search_by_cpf(input) : gateway.search_by_registry(input)

      if resultado && !resultado.strip.empty?
        puts "✅ Resultado encontrado no ano #{ano}!"
        puts resultado
        salvar_html("#{tipo}_#{input}_#{ano}", resultado)
        return
      else
        puts "⚠️  Sem resultado no ano #{ano}."
      end
    rescue => e
      puts "❌ Erro no ano #{ano}: #{e.message}"
    end
  end

  puts "\n❌ Nenhum resultado encontrado em nenhum dos anos de 2010 a 2023."
end

puts "🔍 Modo de busca ENEM por CPF ou Inscrição"
puts "Digite o CPF (11 dígitos) ou número de inscrição (12 dígitos):"

while (print "\n🔢 Entrada: "; input = STDIN.gets.chomp.strip) && !input.empty?
  if input.match?(/^\d{11}$/)
    puts "🔎 Buscando por CPF: #{input}..."
    tentar_consulta_por_anos(input, :cpf)
  elsif input.match?(/^\d{12}$/)
    puts "🔎 Buscando por inscrição: #{input}..."
    tentar_consulta_por_anos(input, :registry)
  else
    puts "❌ Entrada inválida. Digite um CPF (11 dígitos) ou inscrição (12 dígitos)."
  end
end
