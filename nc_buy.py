from random import random
import matplotlib.pyplot as plt
import json
import requests

# Classe Jogo
class Jogo():
    # Construtor da classe
    def __init__(self, name, rating, price):
        # Definição de atributos
        self.name = name
        self.rating = rating
        self.price = price

# Classe individuos, uma população é um conjunto de individuos        
class Individuo():
    def __init__(self, espacos, valores, limite_espacos, geracao=0):
        # Definição de atributos
        self.espacos = espacos
        self.valores = valores
        self.limite_espacos = limite_espacos
        self.nota_avaliacao = 0
        self.espaco_usado = 0
        self.geracao = geracao
        self.cromossomo = [] # Sequencias de 0 e 1's que representam uma solução
        
        # Preenche os cromossomos de forma aleatória
        for i in range(len(espacos)):
            if random() < 0.88: # 88% de chance de por 0 pois a list de jogos é mt grande
                self.cromossomo.append("0")
            else:
                self.cromossomo.append("1")
                
    # Método de avaliação, maneira de avaliar a solução gerada.
    def avaliacao(self):
        nota = 0
        soma_espacos = 0
        # Procura em cada gene do cromossomo os valores que foram selecionados (==1)
        for i in range(len(self.cromossomo)):
           if self.cromossomo[i] == '1':
                if (self.valores[i] > 90):
                    # peso mt maior pra quando a nota for > 90 
                    nota += self.valores[i] * 10
                else:
                    # penalizacao pra quando for menor
                    nota += self.valores[i] - 68
                soma_espacos += self.espacos[i]
        # Se o resultado da somatório for maior do que o limite que foi indicado, a solução recebe a nota 1 como padrão.
        if soma_espacos > self.limite_espacos:
            nota = 1
        # Carregamos os atributos com a avaliação
        self.nota_avaliacao = nota
        self.espaco_usado = soma_espacos
        
    # Método crossover (reprodução) Operador Genético
    def crossover(self, outro_individuo):
        # Define posição do corte para o cruzamento
        corte = round(random()  * len(self.cromossomo))
        
        # Cria primeiro filho usando a posição de corte e o cromosso dos pais
        filho1 = outro_individuo.cromossomo[0:corte] + self.cromossomo[corte::]
        # Cria segundo filho usando a posição de corte e o cromosso dos pais
        filho2 = self.cromossomo[0:corte] + outro_individuo.cromossomo[corte::]
        
        # Criamos uma lista de objetos do tipo Idividuo para receber a nova geração de cromossomos
        filhos = [Individuo(self.espacos, self.valores, self.limite_espacos, self.geracao + 1),
                  Individuo(self.espacos, self.valores, self.limite_espacos, self.geracao + 1)]
        # Inicializo a nova geração com os filhos que foram criados
        filhos[0].cromossomo = filho1
        filhos[1].cromossomo = filho2
        # Retorna lista com individuos
        return filhos
    
    # Método mutação Operador Genético (diversidade)
    def mutacao(self, taxa_mutacao):
        # Percorre todos os genes do cromossomo        
        for i in range(len(self.cromossomo)):
            # Verifica se executa uma mutação (taxa de mutação é passada como parâmetro)
            if random() < taxa_mutacao: # 0.01 1%
                # Subistitui valores, se 0 -> 1 se 1 -> 0
                if self.cromossomo[i] == '1':
                    self.cromossomo[i] = '0'
                else:
                    self.cromossomo[i] = '1'
                         

        return self
# Criamos a classe principal do projeto
class AlgoritmoGenetico():
    # Criamos o contrutor da classe, que recebe como parâmetro o tamanho da população
    # que será o numero de individuos que queremos criar.
    def __init__(self, tamanho_populacao):
        self.tamanho_populacao = tamanho_populacao
        # Lista para objetos do Individuo
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0
        self.lista_solucoes = []
        
    # Método de criação da População
    def inicializa_populacao(self, espacos, valores, limite_espacos):
        # Inicializo a população
        for i in range(self.tamanho_populacao):
            self.populacao.append(Individuo(espacos, valores, limite_espacos))
        self.melhor_solucao = self.populacao[0]
    
    # Avalia a poplação de acordo com a nota (valor do individuo) (ordena do maior para o menor)
    def ordena_populacao(self):
        self.populacao = sorted(self.populacao,
                                key = lambda populacao: populacao.nota_avaliacao,
                                reverse = True)
    
    # Método para buscar o melhor individuo
    def melhor_individuo(self, individuo):
        if individuo.nota_avaliacao > self.melhor_solucao.nota_avaliacao:
            self.melhor_solucao = individuo
    
    # Método para somar todas as notas de uma população    
    def soma_avaliacoes(self):
        soma = 0
        for individuo in self.populacao:
           soma += individuo.nota_avaliacao
        return soma
    
    # Método de seleção de pais para geração da proxima geração (roleta viciada)
    # Retorna o indice do array que foi selecionado
    def seleciona_pai(self, soma_avaliacao):
        pai = -1
        # Sorteia um dos valores na roleta
        valor_sorteado = random() * soma_avaliacao
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].nota_avaliacao
            pai += 1
            i += 1
        return pai
    
    # Método para visualização dos cromossomos durante as gerações
    def visualiza_geracao(self):
        # Como o vetor está ordenado, usamos a posição 0
        melhor = self.populacao[0]
        print("G:%s -> Nota: %s Preço: %s Cromossomo: %s" % (self.populacao[0].geracao,
                                                               melhor.nota_avaliacao,
                                                               melhor.espaco_usado,
                                                               melhor.cromossomo))
    
    # 
    def resolver(self, taxa_mutacao, numero_geracoes, espacos, valores, limite_espacos):
        # Inicializa uma população
        self.inicializa_populacao(espacos, valores, limite_espacos)
        # Avaliação da população
        for individuo in self.populacao:
            individuo.avaliacao()
        # Ordenação da população
        self.ordena_populacao()
        self.melhor_solucao = self.populacao[0]
        # Insere valores na lista para usar no grafico
        self.lista_solucoes.append(self.melhor_solucao.nota_avaliacao)
        
        self.visualiza_geracao()
        # Roda o loop do algoritmo genetico até atender o critério de parada
        # (seleção dos pais, geração dos filhos, crossover, mutação)
        for geracao in range(numero_geracoes):
            # Somatório para seleção dos pais da nova geração
            soma_avaliacao = self.soma_avaliacoes()            
            nova_populacao = []
            # Faz a combinação dos pais (Roleta)
            for individuos_gerados in range(0, self.tamanho_populacao, 2):
                # Seleção dos pais
                pai1 = self.seleciona_pai(soma_avaliacao)
                pai2 = self.seleciona_pai(soma_avaliacao)
                # Criação dos filhos
                filhos = self.populacao[pai1].crossover(self.populacao[pai2])
                # Nova Geração de individuos
                nova_populacao.append(filhos[0].mutacao(taxa_mutacao))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao))
            # Substituição da população antiga
            self.populacao = list(nova_populacao)
            # Avaliação dos individuos
            for individuo in self.populacao:
                individuo.avaliacao()
            # Ordenação dos melhores
            self.ordena_populacao()
            # Visualização dos individuos
            self.visualiza_geracao()
            # Busca pela melhor solução
            melhor = self.populacao[0]
            # Popula lista do grafico
            self.lista_solucoes.append(melhor.nota_avaliacao)
            self.melhor_individuo(melhor)
        
        # Imprime a melhor solução ao final do processo
        print("\nMelhor solução -> Geração: %s Notas: %s Custo: %s Cromossomo: %s" %
              (self.melhor_solucao.geracao,
               self.melhor_solucao.nota_avaliacao,
               self.melhor_solucao.espaco_usado,
               self.melhor_solucao.cromossomo))
        return self.melhor_solucao.cromossomo

def getDatabase(new=False):

    if new:
        api_key = '57a62b6e27412ebc96becd4198959412'
        jogos = []
        pages = [0,1,2,3,4] # * 20 por pagina = 100 jogos
        for page in pages:
            r = requests.get('https://api-savecoins.nznweb.com.br/v1/games?currency=BRL&filter[platform]=nintendo&locale=en&page[number]={}&page[size]=20'.format(page))
            raw_games = json.loads(r.content)
            next_url = raw_games['links']['next']
            for game in raw_games['data']:
                try:
                    query = 'fields name, rating; where ( release_dates.platform = 130 & name ~ *"{}"*);'.format(game['title'])
                    game_r = requests.post('https://api-v3.igdb.com/games/', data=query, headers={'user-key': api_key})
                    game_r = json.loads(game_r.content)
                    print(game['title'], game_r)
                    if (game['price_info'] is not None) and len(game_r) > 0:
                        to_jogos = {'name': game_r[0]['name'], 'rating':game_r[0]['rating'], 'price':game['price_info']['rawCurrentPrice']}
                        print(to_jogos)
                        jogos.append(to_jogos)
                        print('OK\nn')
                    else:
                        raise IndexError()
                        print('Jogo sem preço')
                except IndexError:
                    print('Deu ruim tentando com:', game['title'].split(' ')[0])
                    query = 'fields name, rating; where ( release_dates.platform = 130 & name ~ *"{}"*);'.format(game['title'].split(' ')[0])
                    game_r = requests.post('https://api-v3.igdb.com/games/', data=query, headers={'user-key': api_key})
                    game_r = json.loads(game_r.content)
                    print(game['title'], game_r, game)
                    if (game['price_info'] is not None) and len(game_r) > 0:
                        to_jogos = {'name': game_r[0]['name'], 'rating':game_r[0]['rating'], 'price':game['price_info']['rawCurrentPrice']}
                        print(to_jogos)
                        jogos.append(to_jogos)
                        print('OK\nn')
                    else:
                        print('Jogo sem preço')
                except KeyError:
                    print("Sem nota :(", game['title'])
                except TypeError:
                    print('Nem sei que que deu, só nao quero que quebre denovo')


        with open('games.json', 'w') as outfile:
            print(jogos, len(jogos))
            json.dump(jogos, outfile)
            return jogos
    else:
        with open('games.json') as json_file:
            data = json.load(json_file)
            return data


# Função main do projeto
if __name__ == '__main__':

    # passar true caso queira popular o json denovo
    games = (getDatabase(new=True))
    lista_de_jogos = []
    for game in games:
        lista_de_jogos.append(Jogo(name=game['name'], rating=game['rating'], price=game['price']))

    
    # Criamos uma lista para armazenar as informações do jogos
    price = [] # limte de preço
    rating = [] # o que quero maior
    nomes = []
    # Inicializamos as listas
    for jogo in lista_de_jogos:
        price.append(jogo.price)
        rating.append(jogo.rating)
        nomes.append(jogo.name)

    #### PARAMETRO DE BUSCA DO ALGORITMO ####
    # Neste caso 1000 reais, não funciona mt bem pra  valores inferiores a 320 reais
    limite = 1000
    
    #### AJUSTE DE PARAMETROS DO ALGORITMO ####
    # Criamos 100 Individuos
    tamanho_populacao = 100
    # Taxa de mutação em 1%
    taxa_mutacao = 0.01
    # Total de tentativas para encontrar a resposta
    numero_geracoes = 1000
    #### AJUSTE DE PARAMETROS DO ALGORITMO ####

    # Cria um objeto da classe AlgoritmoGenetico
    ag = AlgoritmoGenetico(tamanho_populacao)
    # Chama o método resolver onde passamos os parametros do algoritmo
    # Resolver terá o cromossomo com a melhor solução encontrada
    resultado = ag.resolver(taxa_mutacao, numero_geracoes, price, rating, limite)
    # Para visualizar os itens que foram selecionados
    count = 0
    price_t = 0
    print("\n\n\nDado o preço limite de R${} a lista de jogos recomentada com melhores notas é:".format(limite))
    for i in range(len(lista_de_jogos)):
        if resultado[i] == '1':
            print("Nome: %s R$ %s Nota %s" % (lista_de_jogos[i].name,
                                       lista_de_jogos[i].price, lista_de_jogos[i].rating))
            count += 1
            price_t += lista_de_jogos[i].price
    print("Número de jogos: {} preço total: {}".format(count, price_t))
    # Mostra os valores em um grafico durante as gerações
    plt.plot(ag.lista_solucoes)
    plt.title("Acompanhamento dos valores")
    plt.show()
