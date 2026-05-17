# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

import sys
import io
import json

class LinhaDescartada(Exception):
    pass

# Força saída UTF-8 no console do Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Importamos o analisador da Fase 1 para ler o arquivo e extrair os tokens.
# Renomeamos de "analisador.py" para "lexico.py" para evitar confusão com o de análise sintática.
from lexico import Token, lerArquivo, parseExpressao, salvarArquivo

def construirGramatica():
    """
    Define as regras de produção da linguagem RPN em formato LL(1).
    Retorna um dicionário com gramática, FIRST, FOLLOW e tabela LL(1).
    """

    # Regras de produção: { nao_terminal: [[producao1], [producao2], ...] }
    regras_producao = {
        "programa": [
            ["comando_lista"]
        ],
        "comando_lista": [
            ["comando", "comando_lista"],
            ["ε"]
        ],
        "comando": [
            ["ABRE_PAREN", "conteudo_comando", "FECHA_PAREN"]
        ],
        "conteudo_comando": [
            ["KEYWORD_START"],
            ["KEYWORD_END"],
            ["NUMERO", "sufixo_numero"],
            ["MEMORIA", "sufixo_memoria"],
            ["comando", "sufixo_comando"]
        ],
        "sufixo_numero": [
            ["KEYWORD_RES"],
            ["NUMERO", "operador_final"],
            ["MEMORIA", "apos_mem"],
            ["comando", "operador_final"]
        ],
        "sufixo_memoria": [
            ["NUMERO", "operador_final"],
            ["MEMORIA", "apos_mem"],
            ["comando", "operador_final"],
            ["ε"]
        ],
        "sufixo_comando": [
            ["NUMERO", "operador_final"],
            ["MEMORIA", "apos_mem"],
            ["comando", "apos_cmd"],
            ["ε"]
        ],
        "operador_final": [
            ["OPERADOR"],
            ["OPERADOR_REL"]
        ],
        "apos_mem": [
            ["OPERADOR"],
            ["OPERADOR_REL"],
            ["ε"]
        ],
        "apos_cmd": [
            ["OPERADOR"],
            ["OPERADOR_REL"],
            ["KEYWORD_WHILE"],
            ["comando", "KEYWORD_IF"]
        ]
    }

    # Lista de todos os terminais reconhecidos pelo léxico
    lista_terminais = [
        "ABRE_PAREN", "FECHA_PAREN", "NUMERO", "OPERADOR",
        "OPERADOR_REL", "MEMORIA", "KEYWORD_START", "KEYWORD_END",
        "KEYWORD_RES", "KEYWORD_IF", "KEYWORD_WHILE", "$"
    ]

    # Calcula FIRST, FOLLOW e tabela LL(1)
    conjuntos_first = calcularFirst(regras_producao, lista_terminais)
    conjuntos_follow = calcularFollow(regras_producao, conjuntos_first, lista_terminais)
    tabela_ll1 = construirTabelaLL1(regras_producao, conjuntos_first, conjuntos_follow, lista_terminais)

    # Valida ausência de conflitos
    eh_valida = validarGramaticaLL1(tabela_ll1)

    resultado_gramatica = {
        "gramatica": regras_producao,
        "terminais": lista_terminais,
        "first": conjuntos_first,
        "follow": conjuntos_follow,
        "tabela_ll1": tabela_ll1,
        "eh_valida": eh_valida
    }

    return resultado_gramatica

def calcularFirst(regras_producao, lista_terminais):
    """
    Calcula os conjuntos FIRST para cada não-terminal usando algoritmo de ponto fixo.
    """
    conjuntos_first = {}

    # Inicializa conjuntos FIRST vazios para cada não-terminal
    for nao_terminal in regras_producao:
        conjuntos_first[nao_terminal] = set()

    # Algoritmo de ponto fixo: repete até não haver mudanças
    houve_mudanca = True
    while houve_mudanca:
        houve_mudanca = False

        for nao_terminal in regras_producao:
            for producao in regras_producao[nao_terminal]:
                # Calcula FIRST da produção e adiciona ao não-terminal
                first_da_producao = calcularFirstDeProducao(producao, conjuntos_first, lista_terminais)

                tamanho_anterior = len(conjuntos_first[nao_terminal])
                conjuntos_first[nao_terminal] = conjuntos_first[nao_terminal].union(first_da_producao)

                if len(conjuntos_first[nao_terminal]) > tamanho_anterior:
                    houve_mudanca = True

    return conjuntos_first

def calcularFirstDeProducao(producao, conjuntos_first, lista_terminais):
    """
    Calcula o conjunto FIRST de uma sequência de símbolos (produção).
    """
    resultado_first = set()

    # Produção vazia
    if producao == ["ε"]:
        resultado_first.add("ε")
        return resultado_first

    for simbolo in producao:
        # Se é terminal, adiciona e para
        if simbolo in lista_terminais or simbolo == "ε":
            resultado_first.add(simbolo)
            break

        # Se é não-terminal, adiciona FIRST dele (sem ε)
        if simbolo in conjuntos_first:
            resultado_first = resultado_first.union(conjuntos_first[simbolo] - {"ε"})

            # Se ε não está em FIRST do símbolo, para aqui
            if "ε" not in conjuntos_first[simbolo]:
                break
        else:
            # Símbolo desconhecido tratado como terminal
            resultado_first.add(simbolo)
            break
    else:
        # Todos os símbolos podem derivar ε
        resultado_first.add("ε")

    return resultado_first

def calcularFollow(regras_producao, conjuntos_first, lista_terminais):
    """
    Calcula os conjuntos FOLLOW para cada não-terminal.
    O símbolo inicial 'programa' inclui $ no FOLLOW.
    """
    conjuntos_follow = {}

    # Inicializa conjuntos FOLLOW vazios
    for nao_terminal in regras_producao:
        conjuntos_follow[nao_terminal] = set()

    # Regra 1: $ pertence a FOLLOW do símbolo inicial
    conjuntos_follow["programa"].add("$")

    # Algoritmo de ponto fixo
    houve_mudanca = True
    while houve_mudanca:
        houve_mudanca = False

        for nao_terminal in regras_producao:
            for producao in regras_producao[nao_terminal]:
                if producao == ["ε"]:
                    continue

                for indice_simbolo, simbolo in enumerate(producao):
                    # Só calcula FOLLOW para não-terminais na produção
                    if simbolo not in regras_producao:
                        continue

                    # Pega o resto da produção após o símbolo atual
                    resto_producao = producao[indice_simbolo + 1:]

                    if resto_producao:
                        # Regra 2: FIRST(resto) - {ε} vai para FOLLOW(simbolo)
                        first_do_resto = calcularFirstDeProducao(resto_producao, conjuntos_first, lista_terminais)

                        tamanho_anterior = len(conjuntos_follow[simbolo])
                        conjuntos_follow[simbolo] = conjuntos_follow[simbolo].union(first_do_resto - {"ε"})

                        # Regra 3: Se ε ∈ FIRST(resto), FOLLOW(nao_terminal) vai para FOLLOW(simbolo)
                        if "ε" in first_do_resto:
                            conjuntos_follow[simbolo] = conjuntos_follow[simbolo].union(conjuntos_follow[nao_terminal])

                        if len(conjuntos_follow[simbolo]) > tamanho_anterior:
                            houve_mudanca = True
                    else:
                        # Regra 3: Símbolo está no final da produção
                        tamanho_anterior = len(conjuntos_follow[simbolo])
                        conjuntos_follow[simbolo] = conjuntos_follow[simbolo].union(conjuntos_follow[nao_terminal])

                        if len(conjuntos_follow[simbolo]) > tamanho_anterior:
                            houve_mudanca = True

    return conjuntos_follow

def construirTabelaLL1(regras_producao, conjuntos_first, conjuntos_follow, lista_terminais):
    """
    Constrói a tabela de análise LL(1).
    Retorna dicionário { (nao_terminal, terminal): producao }.
    Se houver conflito, armazena lista de produções.
    """
    tabela_ll1 = {}

    for nao_terminal in regras_producao:
        for producao in regras_producao[nao_terminal]:
            # Calcula FIRST da produção
            first_da_producao = calcularFirstDeProducao(producao, conjuntos_first, lista_terminais)

            # Para cada terminal em FIRST(produção), adiciona na tabela
            for terminal in first_da_producao:
                if terminal == "ε":
                    continue

                chave_tabela = (nao_terminal, terminal)

                if chave_tabela in tabela_ll1:
                    # Conflito detectado: armazena ambas as produções
                    entrada_existente = tabela_ll1[chave_tabela]
                    if isinstance(entrada_existente[0], list):
                        entrada_existente.append(producao)
                    else:
                        tabela_ll1[chave_tabela] = [entrada_existente, producao]
                else:
                    tabela_ll1[chave_tabela] = producao

            # Se ε ∈ FIRST(produção), para cada terminal em FOLLOW(nao_terminal)
            if "ε" in first_da_producao:
                for terminal_follow in conjuntos_follow.get(nao_terminal, set()):
                    chave_tabela = (nao_terminal, terminal_follow)

                    if chave_tabela in tabela_ll1:
                        entrada_existente = tabela_ll1[chave_tabela]
                        if isinstance(entrada_existente[0], list):
                            entrada_existente.append(producao)
                        else:
                            tabela_ll1[chave_tabela] = [entrada_existente, producao]
                    else:
                        tabela_ll1[chave_tabela] = producao

    return tabela_ll1

def validarGramaticaLL1(tabela_ll1):
    """
    Verifica se a tabela LL(1) possui conflitos.
    Retorna True se a gramática é LL(1) válida, False caso contrário.
    """
    conflitos_encontrados = []

    for chave_tabela, producao in tabela_ll1.items():
        # Conflito = célula com lista de listas (múltiplas produções)
        if isinstance(producao[0], list):
            nao_terminal, terminal = chave_tabela
            conflito_texto = f"Conflito em M[{nao_terminal}, {terminal}]: {producao}"
            conflitos_encontrados.append(conflito_texto)

    if conflitos_encontrados:
        print("ERRO: A gramática NÃO é LL(1). Conflitos encontrados:")
        for conflito in conflitos_encontrados:
            print(f"  - {conflito}")
        return False

    print("Gramática validada: é LL(1) sem conflitos.")
    return True

def exibirGramatica(resultado_gramatica):
    """
    Imprime a gramática, FIRST, FOLLOW e tabela LL(1) formatados.
    """
    regras_producao = resultado_gramatica["gramatica"]
    conjuntos_first = resultado_gramatica["first"]
    conjuntos_follow = resultado_gramatica["follow"]
    tabela_ll1 = resultado_gramatica["tabela_ll1"]

    # Exibe regras de produção
    print("=" * 60)
    print("REGRAS DE PRODUÇÃO")
    print("=" * 60)
    for nao_terminal, producoes in regras_producao.items():
        for indice_producao, producao in enumerate(producoes):
            separador = "::=" if indice_producao == 0 else "  |"
            texto_producao = " ".join(producao)
            print(f"  {nao_terminal:<20} {separador} {texto_producao}")
    print()

    # Exibe conjuntos FIRST
    print("=" * 60)
    print("CONJUNTOS FIRST")
    print("=" * 60)
    for nao_terminal in regras_producao:
        elementos_ordenados = sorted(conjuntos_first[nao_terminal])
        texto_first = "{ " + ", ".join(elementos_ordenados) + " }"
        print(f"  FIRST({nao_terminal:<20}) = {texto_first}")
    print()

    # Exibe conjuntos FOLLOW
    print("=" * 60)
    print("CONJUNTOS FOLLOW")
    print("=" * 60)
    for nao_terminal in regras_producao:
        elementos_ordenados = sorted(conjuntos_follow[nao_terminal])
        texto_follow = "{ " + ", ".join(elementos_ordenados) + " }"
        print(f"  FOLLOW({nao_terminal:<20}) = {texto_follow}")
    print()

    # Exibe tabela LL(1)
    print("=" * 60)
    print("TABELA DE ANÁLISE LL(1)")
    print("=" * 60)
    # Agrupa por não-terminal para exibir organizado
    nao_terminais_unicos = list(regras_producao.keys())
    for nao_terminal in nao_terminais_unicos:
        entradas_deste_nt = []
        for (nt_chave, terminal), producao in tabela_ll1.items():
            if nt_chave == nao_terminal:
                texto_producao = " ".join(producao)
                entradas_deste_nt.append((terminal, texto_producao))

        if entradas_deste_nt:
            entradas_deste_nt.sort(key=lambda entrada: entrada[0])
            for terminal, texto_producao in entradas_deste_nt:
                print(f"  M[{nao_terminal:<20}, {terminal:<15}] = {texto_producao}")
    print()

def gerarTokens(linhas_brutas):
    """
    Gera tokens a partir das linhas brutas usando o léxico e salva em tokens.txt.
    """
    linhas_tokens = []

    for linha in linhas_brutas:
        vetor_tokens = []

        # Gera os tokens usando léxico -> armazena em vetor_tokens
        parseExpressao(linha, vetor_tokens)

        if vetor_tokens:
            # Formata -> TIPO:VALOR
            tokens_formatados = []
            for token in vetor_tokens:
                tokens_formatados.append(f"{token.tipo}:{token.valor}")

            # Junta com espaços e adiciona a lista de linhas de tokens
            linha_completa = " ".join(tokens_formatados)
            linhas_tokens.append(linha_completa)

    # Utiliza função do léxico para salvar o arquivo tokens.txt
    salvarArquivo('tokens.txt', linhas_tokens)

def lerTokens(nome_arquivo):
    """
    Lê o arquivo tokens.txt e retorna lista de listas de Token.
    """
    lista_de_linhas = []
    numero_linha = 1

    try:
        with open(nome_arquivo, 'r') as arquivo_texto:
            for linha_bruta in arquivo_texto:
                # Validação extra (analisar necessidade depois)
                linha_limpa = linha_bruta.strip() # remove espaços em branco (como implementado no léxico)
                if not linha_limpa:
                    numero_linha += 1
                    continue # pula linhas vazias

                tokens_da_linha = []

                # Divide a linha pelos espaços para pegar cada "TIPO:VALOR"
                pedacos_de_texto = linha_limpa.split(' ')

                for pedaco in pedacos_de_texto:
                    # Divide entre tipo e valor usando o separador ":"
                    if ':' in pedaco:
                        tipo_extraido, valor_extraido = pedaco.split(':', 1)

                        # Validação básica de tokens
                        if tipo_extraido == "ERRO":
                            print(f"Erro léxico na linha {numero_linha}: {valor_extraido} -> Descartando a linha inteira.\n")
                            # Substitui a linha por uma casca vazia para acionar o pânico no parser sem quebrar a lista
                            t1 = Token("ABRE_PAREN", "("); t1.linha = numero_linha
                            t2 = Token("LINHA_INVALIDA", f"Erro léxico ({valor_extraido})"); t2.linha = numero_linha
                            t3 = Token("FECHA_PAREN", ")"); t3.linha = numero_linha
                            tokens_da_linha = [t1, t2, t3]
                            break

                        # Cria o objeto Token (usando a classe importada do lexico.py)
                        novo_token = Token(tipo_extraido, valor_extraido)
                        novo_token.linha = numero_linha
                        tokens_da_linha.append(novo_token)

                if tokens_da_linha:
                    lista_de_linhas.append(tokens_da_linha)

                numero_linha += 1

        return lista_de_linhas

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        sys.exit(1)

def parsear(linhas_de_tokens, tabela_ll1):
    """
    Inicia a análise sintática descendente recursiva usando a tabela LL(1).
    Mantém uma pilha de análise explícita para controle do parsing,
    combinada com funções recursivas para cada não-terminal.
    """
    # Juntar a lista de listas em uma única lista
    lista_tokens = []
    
    for tokens_da_linha in linhas_de_tokens:
        for token_extraido in tokens_da_linha:
            lista_tokens.append(token_extraido)
            
    # Adiciona o token de fim de arquivo ($) na última posição
    token_fim = Token("$", "$")
    token_fim.linha = -1 # Marcador de fim de arquivo
    lista_tokens.append(token_fim)

    indice_atual = 0

    # Topo da pilha = último elemento da lista (índice -1)
    # Inicializa com o marcador de final ($) e o símbolo inicial (programa)
    pilha_analise = ["$", "programa"]

    def exibirPilha():
        """Exibe o estado atual da pilha (topo à esquerda)."""
        conteudo = " | ".join(reversed(pilha_analise))
        print(f"  [Pilha] topo → [ {conteudo} ] ← final")

    def consumirToken(tipo_esperado):
        nonlocal indice_atual
        
        # Se o indice extrapolou, nao podemos consumir 
        if indice_atual >= len(lista_tokens):
            return False
            
        token_analisado = lista_tokens[indice_atual]
        
        # Valida se é TIPO (NUMERO) ou o VALOR exato ($)
        if token_analisado.tipo == tipo_esperado or token_analisado.valor == tipo_esperado or token_analisado.tipo == f"KEYWORD_{tipo_esperado}":
            # Remove o terminal do topo da pilha de análise
            if pilha_analise and pilha_analise[-1] == tipo_esperado:
                pilha_analise.pop()
            print(f"  [Match] Casou token: {token_analisado.valor} (referência: {tipo_esperado})")
            exibirPilha()
            indice_atual += 1
            return True
            
        print(f"  [Erro] Esperava '{tipo_esperado}', mas obteve token '{token_analisado.valor}'.")
        return False

    print("parsing\n")
    print(f"-> Quantidade de tokens inseridos na fita de leitura: {len(lista_tokens)}")
    
    # (Bloco informativo, pode ser removido)
    textos_dos_tokens = []
    tipos_literais = ["OPERADOR", "OPERADOR_REL", "ABRE_PAREN", "FECHA_PAREN", "$"]
    
    for token in lista_tokens:
        if token.tipo in tipos_literais:
            textos_dos_tokens.append(token.valor) 
        else:
            textos_dos_tokens.append(token.tipo)  
            
    fita_formatada = " ".join(textos_dos_tokens)
    print(f"-> Fita pronta: {fita_formatada}")
    print(f"-> Pilha inicial: [ programa | $ ]\n")

    def acionarModoPanico(nao_terminal_afetado):
        nonlocal indice_atual
        if indice_atual < len(lista_tokens):
            token_com_erro = lista_tokens[indice_atual]
            linha_erro = getattr(token_com_erro, 'linha', None)
            print(f"  [Recuperação Pânico] Erro no token '{token_com_erro.valor}'. Abortando a linha {linha_erro}.")
            raise LinhaDescartada()

    def derivarNaoTerminal(nome_nao_terminal):
        nonlocal indice_atual
        
        # Previne acesso fora dos limites caso a fita termine inesperadamente
        if indice_atual >= len(lista_tokens):
            return {"nodo_pai": nome_nao_terminal, "erro": "Fim inesperado da fita de tokens"}
            
        token_analisado = lista_tokens[indice_atual]
        chave_de_busca = (nome_nao_terminal, token_analisado.tipo)
        
        if chave_de_busca in tabela_ll1:
            producao_encontrada = tabela_ll1[chave_de_busca]

            # Remove o não-terminal do topo (foi selecionado para expansão)
            if pilha_analise and pilha_analise[-1] == nome_nao_terminal:
                pilha_analise.pop()

            # Empilha símbolos da produção em ordem REVERSA (o primeiro símbolo da produção fica no topo)
            simbolos_para_empilhar = [s for s in producao_encontrada if s != "ε"]
            for simbolo in reversed(simbolos_para_empilhar):
                pilha_analise.append(simbolo)

            nodo_arvore = {"nodo_pai": nome_nao_terminal, "producao_acionada": " ".join(producao_encontrada), "nodos_filhos": []}
            print(f"  [Derivação] {nome_nao_terminal} -> {nodo_arvore['producao_acionada']}")
            exibirPilha()
            
            for simbolo_producao in producao_encontrada:
                if simbolo_producao == "ε":
                    nodo_arvore["nodos_filhos"].append({"terminal_folha": "ε"})
                    continue
                    
                # Se for um não terminal, temos uma função especifica mapeada para ele
                if simbolo_producao in mapa_funcoes_recursivas: 
                    funcao_recursiva_filho = mapa_funcoes_recursivas[simbolo_producao]
                    filho_gerado_na_arvore = funcao_recursiva_filho()
                    
                    if filho_gerado_na_arvore:
                        nodo_arvore["nodos_filhos"].append(filho_gerado_na_arvore)
                else: 
                    # Se não é terminal, usamos a função consumirToken para validar e extrair o token
                    casou_sucesso = consumirToken(simbolo_producao)
                    if casou_sucesso:
                        # Extrai posição - 1 pois o token acabou de ser validado e somou na fita
                        nodo_arvore["nodos_filhos"].append({
                            "terminal_folha": simbolo_producao, 
                            "valor_extraido": lista_tokens[indice_atual - 1].valor
                        })
                    else:
                        nodo_arvore["nodos_filhos"].append({"erro_sintatico": f"Faltou terminal esperado {simbolo_producao}"})
                        acionarModoPanico(nome_nao_terminal)
                        
            return nodo_arvore
        else:
            print(f"  [Erro Sintático] Fluxo de regras quebrado em '{nome_nao_terminal}', elemento não aguardava o token '{token_analisado.valor}' (de perfil {token_analisado.tipo}).")
            acionarModoPanico(nome_nao_terminal)
            return {"erro_nodo_pai": nome_nao_terminal, "falha_registro": token_analisado.valor}

    # Funções de Não-Terminais
    def parsePrograma(): 
        return derivarNaoTerminal("programa")

    def parseComandoLista(): 
        return derivarNaoTerminal("comando_lista")
        
    def parseComando(): 
        nonlocal indice_atual
        indice_inicio = indice_atual
        try:
            return derivarNaoTerminal("comando")
        except LinhaDescartada:
            # Captura a exceção no escopo do comando e pula o resto da linha
            if indice_inicio < len(lista_tokens):
                linha_erro = getattr(lista_tokens[indice_inicio], 'linha', -1)
                while indice_atual < len(lista_tokens):
                    t = lista_tokens[indice_atual]
                    if getattr(t, 'linha', None) != linha_erro or t.tipo == "$":
                        break
                    indice_atual += 1
            return {"nodo_pai": "comando_descartado", "motivo": "Erro Sintático ou Léxico na linha", "nodos_filhos": []}
            
    def parseConteudoComando(): 
        return derivarNaoTerminal("conteudo_comando")

    def parseSufixoNumero(): 
        return derivarNaoTerminal("sufixo_numero")

    def parseSufixoMemoria(): 
        return derivarNaoTerminal("sufixo_memoria")

    def parseSufixoComando(): 
        return derivarNaoTerminal("sufixo_comando")

    def parseOperadorFinal(): 
        return derivarNaoTerminal("operador_final")

    def parseAposMem(): 
        return derivarNaoTerminal("apos_mem")
        
    def parseAposCmd(): 
        return derivarNaoTerminal("apos_cmd")
    
    # Dicionário dinâmico conectando texto as funções 
    mapa_funcoes_recursivas = {
        "programa": parsePrograma,
        "comando_lista": parseComandoLista,
        "comando": parseComando,
        "conteudo_comando": parseConteudoComando,
        "sufixo_numero": parseSufixoNumero,
        "sufixo_memoria": parseSufixoMemoria,
        "sufixo_comando": parseSufixoComando,
        "operador_final": parseOperadorFinal,
        "apos_mem": parseAposMem,
        "apos_cmd": parseAposCmd
    }

    # Inicialização central do parser
    arvore_sintatica_ast = parsePrograma()
    
    # Pós-processamento: Varre a árvore para converter comandos quebrados em nós de descarte
    def limparArvore(no):
        if "nodos_filhos" in no:
            tem_erro = False
            msg_erro = ""
            
            # Sub-rotina para procurar qualquer assinatura de falha nos filhos
            def buscarErro(n):
                nonlocal tem_erro, msg_erro
                if "erro_sintatico" in n or "erro_nodo_pai" in n:
                    tem_erro = True
                    msg_erro = "Erro Sintático"
                elif n.get("terminal_folha") == "LINHA_INVALIDA":
                    tem_erro = True
                    msg_erro = n.get("valor_extraido", "Erro Léxico")
                elif "nodos_filhos" in n:
                    for f in n["nodos_filhos"]:
                        buscarErro(f)
            
            if no.get("nodo_pai") == "comando":
                buscarErro(no)
                if tem_erro:
                    # Transmuta o nó comando em um nó de descarte limpo
                    no["nodo_pai"] = "comando_descartado"
                    no["motivo"] = msg_erro
                    no["nodos_filhos"] = []
                    return
            
            # Se não foi descartado, continua procurando mais abaixo
            for filho in no["nodos_filhos"]:
                limparArvore(filho)
                
    limparArvore(arvore_sintatica_ast)
    
    if indice_atual < len(lista_tokens) and lista_tokens[indice_atual].tipo != "$":
        print(f"\n  [Aviso Analítico] O parsing finalizou através da raiz mas sobraram tokens não processados na fita, a partir do medidor: {lista_tokens[indice_atual].valor}")
    
    print("\n=> Parsing e rastreamento recursivo concluídos com sucesso!")
    return arvore_sintatica_ast # retorna a AST

def construirTextoArvore(no, prefixo="", eh_ultimo=True, eh_raiz=True):
    """
    Percorre a Árvore Sintática de forma recursiva e constrói uma representação
    visual em texto usando caracteres de ramificação (para depois salvar no arquivo .md).
    """
    linhas = []

    # Ignora totalmente nós descartados e seus filhos (linha oculta na árvore)
    if no.get("nodo_pai") == "comando_descartado":
        return []

    # Define o texto do nó lendo as chaves do parser
    if "terminal_folha" in no:
        # Como é um nó folha (terminal) -> extraí o valor com "valor_extraido" e caso não exista, deixa vazio (para evitar None)
        valor = no.get("valor_extraido", "")
        # Exibe o tipo do terminal e o valor correspondente -> como NUMERO (3.14)
        texto_no = f"{no['terminal_folha']} ({valor})"
    elif "nodo_pai" in no:
        # É um nó interno (não-terminal) -> exemplo: comando, sufixo_numero, conteudo_comando, etc
        texto_no = no["nodo_pai"]
    elif "erro_sintatico" in no:
        # Nó folha com erro capturado pelo "Panic Mode"
        texto_no = f"ERRO SINTÁTICO: {no['erro_sintatico']}"
    elif "erro_nodo_pai" in no:
        # Nó pai que falhou na derivação -> nenhuma regra válida na tabela LL(1) para o token
        texto_no = f"FALHA NO NÓ: {no['erro_nodo_pai']} (Token inesperado: {no.get('falha_registro', '')})"
    else:
        # Segurança extra para caso nó venha mal formado
        texto_no = "Nó Desconhecido"

    # Desenha os galhos
    if eh_raiz:
        # A raiz é o ponto de partida, não tenho nenhum galho
        linhas.append(texto_no)
        # Não há linha vertical antes da raiz, então o prefixo para os filhos começa vazio
        novo_prefixo = ""
    else:
        # Caso seja uma folha/último filho
        if eh_ultimo:
            marcador = "└── "
            # Não tem mais irmãos depois -> espaço em branco
            novo_prefixo = prefixo + "    "
        else:
            # Caso ainda tenha irmãos abaixo
            marcador = "├── "
            # Ainda tem irmãos depois -> mantém a linha vertical para conectar
            novo_prefixo = prefixo + "│   "
            

        # Junta o que veio dos anteriores, galho atual, e nome do nó atual
        linhas.append(f"{prefixo}{marcador}{texto_no}")

    # Prepara a lista de filhos para recursão
    if "nodos_filhos" in no: # exemplo: comando -> ABRE_PAREN, conteudo_comando, FECHA_PAREN 
        filhos = no["nodos_filhos"]
    else:
        filhos = []

    # Para o exemplo, temos total_filhos = 3. 
    total_filhos = len(filhos) # contudo, terminal não tem filhos, logo, total_filhos = 0

    # Loop de recursão -> terminais apenas retornam linha do próprio nó, enquanto não-terminais continuam gerando filhos
    for i in range(total_filhos):
        filho = filhos[i]
        
        # Define explicitamente se é o último filho da lista
        if i == (total_filhos - 1):
            ultimo_filho = True
        else:
            ultimo_filho = False
            
        # A recursão passa o novo_prefixo para o nível de baixo e obviamente não é mais raiz
        linhas_filho = construirTextoArvore(filho, novo_prefixo, ultimo_filho, False)

        # Armazena as linhas geradas pelos filhos na lista de linhas do nível atual
        linhas.extend(linhas_filho)

    # Roda para cada nó
    # - Se for um terminal -> for não executou. O return apenas devolve a linha para o pai
    # - Se for um não-terminal -> devolve a lista completa com todos os galhos dos filhos já agrupados
    return linhas

def gerarArvore(derivacao, nome_teste):
    """
    Chama a função construir_texto_arvore para gerar a árvore em formato de string
    e exporta o resultado para o arquivo 'arvore_sintatica.md'.
    """
    nome_arquivo_md = "arvore_sintatica.md"
    nome_arquivo_json = "arvore_sintatica.json"

    try:
        # Passa a derivação para a função que desenha os galhos
        linhas_arvore = construirTextoArvore(derivacao)
        # Junta as linhas da lista em um único texto pulando as linhas
        texto_final = "\n".join(linhas_arvore)

        # Grava no arquivo
        with open(nome_arquivo_md, 'w', encoding='utf-8') as arquivo_md:
            arquivo_md.write("# Árvore Sintática (Derivação)\n\n")
            arquivo_md.write(f"## Resultado do {nome_teste}:\n\n")
            arquivo_md.write("```text\n")
            arquivo_md.write(texto_final + "\n")
            arquivo_md.write("```\n")

        with open(nome_arquivo_json, 'w', encoding='utf-8') as arquivo_json:
            # ensure_ascii=False para manter caracteres como ε
            # indent=4 para deixar o JSON mais legível -> separa em múltiplas linhas
            json.dump(derivacao, arquivo_json, ensure_ascii=False, indent=4)
            
        print(f"Sucesso: Árvore exportada para '{nome_arquivo_md}' e '{nome_arquivo_json}'.")

        arvore_estruturada = derivacao
        return arvore_estruturada

    except Exception as e:
        print(f"Erro ao gerar o arquivo da árvore sintática: {e}")

def coletarTerminais(no):
    """
    Percorre um nó da árvore e coleta todos os terminais (folhas) em ordem.
    Como a árvore respeita a ordem RPN, os terminais já saem na sequência correta
    para processamento (mesma lógica do léxico, só que extraída da árvore).
    """
    terminais = []
    if "terminal_folha" in no:
        terminais.append(no)
    elif "nodos_filhos" in no:
        for filho in no["nodos_filhos"]:
            terminais.extend(coletarTerminais(filho))
    return terminais

def gerarAssembly(arvore, nome_arquivo):
    """
    Percorre a árvore sintática e gera código Assembly ARMv7 (VFP)
    para o ambiente Cpulator-ARMv7 DE1-SoC.
    """

    secao_dados = []
    secao_texto = []
    contador_label = [0]       # lista para permitir modificação dentro das funções internas
    labels_memoria = set()     # variáveis de memória já declaradas no .data
    constantes_usadas = {}     # deduplicação de constantes: valor -> nome_label


    def obterLabelUnico(prefixo):
        """Gera um label único para controle de fluxo."""
        label = f"{prefixo}_{contador_label[0]}"
        contador_label[0] += 1
        return label

    def garantirConstante(valor_texto):
        """Registra uma constante no .data (se ainda não existir) e retorna o nome do label."""
        if valor_texto in constantes_usadas:
            return constantes_usadas[valor_texto]
        nome_label = "const_" + valor_texto.replace(".", "_").replace("-", "neg")
        constantes_usadas[valor_texto] = nome_label
        secao_dados.append("    .align 3")
        secao_dados.append(f"    {nome_label}: .double {valor_texto}")
        return nome_label

    def garantirMemoria(nome_mem):
        """Registra uma variável de memória no .data (se ainda não existir)."""
        nome_label = "mem_" + nome_mem
        if nome_label not in labels_memoria:
            secao_dados.append("    .align 3")
            secao_dados.append(f"    {nome_label}: .double 0.0")
            labels_memoria.add(nome_label)
        return nome_label


    def processarComando(no_comando):
        """
        Processa um nó 'comando' da árvore.
        Extrai os terminais em ordem RPN e gera o Assembly correspondente.
        Retorna o registrador com o resultado (ou None).
        """
        pilha_regs = []
        cont_reg = [0]

        # Busca o nó conteudo_comando dentro do comando
        filhos = no_comando.get("nodos_filhos", [])
        no_conteudo = None
        for filho in filhos:
            if filho.get("nodo_pai") == "conteudo_comando":
                no_conteudo = filho
                break

        if no_conteudo is None:
            return None

        producao = no_conteudo.get("producao_acionada", "")

        # ---- START / END ----
        if producao == "KEYWORD_START":
            secao_texto.append("")
            secao_texto.append("    @ (START) - início do programa")
            return None

        if producao == "KEYWORD_END":
            secao_texto.append("")
            secao_texto.append("    @ (END) - fim do programa")
            return None

        # ---- Detecta se é WHILE ou IF ----
        terminais = coletarTerminais(no_conteudo)
        tipos_terminais = [t.get("terminal_folha", "") for t in terminais]

        if "KEYWORD_WHILE" in tipos_terminais:
            # Estrutura na árvore: conteudo_comando → comando(condição) + sufixo_comando → comando(corpo) + apos_cmd(WHILE)
            label_inicio = obterLabelUnico("while")
            label_fim = f"{label_inicio}_fim"

            # Extrair sub-comandos da árvore
            filhos_conteudo = no_conteudo.get("nodos_filhos", [])
            cmd_condicao = None
            sufixo_cmd = None
            for f in filhos_conteudo:
                if f.get("nodo_pai") == "comando" and cmd_condicao is None:
                    cmd_condicao = f
                elif f.get("nodo_pai") == "sufixo_comando":
                    sufixo_cmd = f

            # Dentro de sufixo_comando, o primeiro 'comando' é o corpo do loop
            cmd_corpo = None
            if sufixo_cmd:
                for f in sufixo_cmd.get("nodos_filhos", []):
                    if f.get("nodo_pai") == "comando":
                        cmd_corpo = f
                        break

            secao_texto.append("")
            secao_texto.append(f"    @ WHILE - início do loop")
            secao_texto.append(f"{label_inicio}:")

            # Processa a condição (gera Assembly do sub-comando e retorna registrador com resultado)
            secao_texto.append(f"    @ Avalia condição do WHILE")
            reg_cond = None
            if cmd_condicao:
                reg_cond = processarComando(cmd_condicao)

            # Compara resultado da condição com 0.0 (falso) → se igual, sai do loop
            if reg_cond:
                nome_zero = garantirConstante("0.0")
                secao_texto.append(f"    LDR R4, ={nome_zero}")
                secao_texto.append(f"    VLDR D15, [R4]              @ 0.0 para comparação")
                secao_texto.append(f"    VCMP.F64 {reg_cond}, D15")
                secao_texto.append(f"    VMRS APSR_nzcv, FPSCR")
                secao_texto.append(f"    BEQ {label_fim}             @ se condição == 0.0 (falso), sai do loop")

            # Processa o corpo do loop
            secao_texto.append(f"    @ Corpo do WHILE")
            if cmd_corpo:
                processarComando(cmd_corpo)

            # Volta ao início do loop
            secao_texto.append(f"    B {label_inicio}               @ volta ao início do loop")
            secao_texto.append(f"{label_fim}:")

            return None

        if "KEYWORD_IF" in tipos_terminais:
            label_else = obterLabelUnico("if_else")
            label_fim = obterLabelUnico("if_fim")

            # Extrair sub-comandos da árvore
            # Estrutura na árvore: conteudo_comando → comando(cond) + sufixo_comando → ( comando(then) + apos_cmd → ( comando(else) + IF ) )
            filhos_conteudo = no_conteudo.get("nodos_filhos", [])
            cmd_condicao = None
            sufixo_cmd = None
            for f in filhos_conteudo:
                if f.get("nodo_pai") == "comando" and cmd_condicao is None:
                    cmd_condicao = f
                elif f.get("nodo_pai") == "sufixo_comando":
                    sufixo_cmd = f

            cmd_then = None
            apos_cmd = None
            if sufixo_cmd:
                for f in sufixo_cmd.get("nodos_filhos", []):
                    if f.get("nodo_pai") == "comando":
                        cmd_then = f
                    elif f.get("nodo_pai") == "apos_cmd":
                        apos_cmd = f

            cmd_else = None
            if apos_cmd:
                for f in apos_cmd.get("nodos_filhos", []):
                    if f.get("nodo_pai") == "comando":
                        cmd_else = f

            secao_texto.append("")
            secao_texto.append(f"    @ IF - Avalia condição")
            reg_cond = None
            if cmd_condicao:
                reg_cond = processarComando(cmd_condicao)

            # Compara resultado com 0.0 (falso) → se igual a falso, pula para o ELSE
            if reg_cond:
                nome_zero = garantirConstante("0.0")
                secao_texto.append(f"    LDR R4, ={nome_zero}")
                secao_texto.append(f"    VLDR D15, [R4]              @ 0.0 para comparação")
                secao_texto.append(f"    VCMP.F64 {reg_cond}, D15")
                secao_texto.append(f"    VMRS APSR_nzcv, FPSCR")
                secao_texto.append(f"    BEQ {label_else}            @ se falso (0.0), pula pro else")

            # Bloco THEN (Verdadeiro)
            secao_texto.append(f"    @ IF - Bloco THEN (Verdadeiro)")
            if cmd_then:
                processarComando(cmd_then)
            secao_texto.append(f"    B {label_fim}               @ fim do then, pula o else")

            # Bloco ELSE (Falso)
            secao_texto.append(f"{label_else}:")
            secao_texto.append(f"    @ IF - Bloco ELSE (Falso)")
            if cmd_else:
                processarComando(cmd_else)

            secao_texto.append(f"{label_fim}:")
            return None

        # Adiciona no assembly comentários para cada comando simples
        pedacos_expr = []
        for t in terminais:
            terminal_atual = t.get("terminal_folha", "")
            if terminal_atual not in ("ε", "ABRE_PAREN", "FECHA_PAREN"):
                valor_atual = t.get("valor_extraido", "")
                if valor_atual != "":
                    pedacos_expr.append(valor_atual)
                else:
                    pedacos_expr.append(terminal_atual)
                    
        expr_str = " ".join(pedacos_expr)
        
        secao_texto.append("")
        secao_texto.append(f" @ Comando RPN: ( {expr_str} ) ")
        for terminal in terminais:
            tipo = terminal.get("terminal_folha", "")
            valor = terminal.get("valor_extraido", "")

            # Pula parênteses e epsilon
            if tipo in ("ABRE_PAREN", "FECHA_PAREN", "ε"):
                continue

            # NUMERO: carrega constante em registrador VFP
            if tipo == "NUMERO":
                nome_const = garantirConstante(valor)
                nome_reg = f"D{cont_reg[0]}"
                cont_reg[0] += 1
                secao_texto.append(f"    LDR R4, ={nome_const}")
                secao_texto.append(f"    VLDR {nome_reg}, [R4]        @ carrega double {valor}")
                pilha_regs.append(nome_reg)

            # OPERADOR: desempilha 2 registradores, opera, empilha resultado
            elif tipo == "OPERADOR":
                if len(pilha_regs) < 2:
                    secao_texto.append(f"    @ ERRO: operandos insuficientes para '{valor}'")
                    continue

                reg_b = pilha_regs.pop()
                reg_a = pilha_regs.pop()
                reg_res = f"D{cont_reg[0]}"
                cont_reg[0] += 1

                if valor == "+":
                    secao_texto.append(f"    VADD.F64 {reg_res}, {reg_a}, {reg_b}    @ {reg_a} + {reg_b}")
                elif valor == "-":
                    secao_texto.append(f"    VSUB.F64 {reg_res}, {reg_a}, {reg_b}    @ {reg_a} - {reg_b}")
                elif valor == "*":
                    secao_texto.append(f"    VMUL.F64 {reg_res}, {reg_a}, {reg_b}    @ {reg_a} * {reg_b}")
                elif valor == "|":
                    secao_texto.append(f"    VDIV.F64 {reg_res}, {reg_a}, {reg_b}    @ divisão real")
                elif valor == "/":
                    secao_texto.append(f"    VDIV.F64 {reg_res}, {reg_a}, {reg_b}    @ divisão inteira")
                    secao_texto.append(f"    VCVT.S32.F64 S31, {reg_res}    @ trunca para inteiro")
                    secao_texto.append(f"    VCVT.F64.S32 {reg_res}, S31    @ volta para double")
                elif valor == "%":
                    secao_texto.append(f"    @ resto: {reg_a} % {reg_b}")
                    secao_texto.append(f"    VDIV.F64 {reg_res}, {reg_a}, {reg_b}")
                    secao_texto.append(f"    VCVT.S32.F64 S31, {reg_res}")
                    secao_texto.append(f"    VCVT.F64.S32 {reg_res}, S31")
                    secao_texto.append(f"    VMUL.F64 {reg_res}, {reg_res}, {reg_b}")
                    secao_texto.append(f"    VSUB.F64 {reg_res}, {reg_a}, {reg_res}    @ resto")
                elif valor == "^":
                    label_pot = obterLabelUnico("potencia")
                    secao_texto.append(f"    @ potenciação: {reg_a} ^ {reg_b}")
                    secao_texto.append(f"    VCVT.S32.F64 S31, {reg_b}")
                    secao_texto.append(f"    VMOV R0, S31              @ R0 = expoente")
                    nome_c1 = garantirConstante("1.0")
                    secao_texto.append(f"    LDR R4, ={nome_c1}")
                    secao_texto.append(f"    VLDR {reg_res}, [R4]    @ resultado = 1.0")
                    secao_texto.append(f"{label_pot}:")
                    secao_texto.append(f"    CMP R0, #0")
                    secao_texto.append(f"    BLE {label_pot}_fim")
                    secao_texto.append(f"    VMUL.F64 {reg_res}, {reg_res}, {reg_a}")
                    secao_texto.append(f"    SUB R0, R0, #1")
                    secao_texto.append(f"    B {label_pot}")
                    secao_texto.append(f"{label_pot}_fim:")

                pilha_regs.append(reg_res)

            # --- OPERADOR_REL: comparação relacional ---
            elif tipo == "OPERADOR_REL":
                if len(pilha_regs) < 2:
                    secao_texto.append(f"    @ ERRO: operandos insuficientes para '{valor}'")
                    continue

                reg_b = pilha_regs.pop()
                reg_a = pilha_regs.pop()
                reg_res = f"D{cont_reg[0]}"
                cont_reg[0] += 1

                label_rel_verdade = obterLabelUnico("rel_verdade")
                label_rel_fim = obterLabelUnico("rel_fim")

                secao_texto.append(f"    @ comparação relacional '{valor}': {reg_a} {valor} {reg_b}")
                secao_texto.append(f"    VCMP.F64 {reg_a}, {reg_b}")
                secao_texto.append(f"    VMRS APSR_nzcv, FPSCR")

                # Lógica Direta: Branch (salta para VERDADE) se a condição bater
                if valor == "<":
                    secao_texto.append(f"    BLT {label_rel_verdade}")
                elif valor == ">":
                    secao_texto.append(f"    BGT {label_rel_verdade}")
                elif valor == "==":
                    secao_texto.append(f"    BEQ {label_rel_verdade}")
                elif valor == "!=":
                    secao_texto.append(f"    BNE {label_rel_verdade}")
                elif valor == "<=":
                    secao_texto.append(f"    BLE {label_rel_verdade}")
                elif valor == ">=":
                    secao_texto.append(f"    BGE {label_rel_verdade}")

                # --- SE A RESPOSTA FOI NÃO (Caiu aqui porque não pulou) ---
                nome_c0 = garantirConstante("0.0")
                secao_texto.append(f"    LDR R4, ={nome_c0}")
                secao_texto.append(f"    VLDR {reg_res}, [R4]        @ false")
                secao_texto.append(f"    B {label_rel_fim}           @ foge do bloco verdade")

                # --- SE A RESPOSTA FOI SIM (Caiu de paraquedas após dar o pulo) ---
                secao_texto.append(f"{label_rel_verdade}:")
                nome_c1 = garantirConstante("1.0")
                secao_texto.append(f"    LDR R4, ={nome_c1}")
                secao_texto.append(f"    VLDR {reg_res}, [R4]        @ true")

                secao_texto.append(f"{label_rel_fim}:")
                pilha_regs.append(reg_res)

            # --- MEMORIA: load ou store (mesmo padrão do léxico) ---
            elif tipo == "MEMORIA":
                nome_label = garantirMemoria(valor)
                if len(pilha_regs) > 0:
                    reg_valor = pilha_regs.pop()
                    secao_texto.append(f"    LDR R0, ={nome_label}        @ store em {valor}")
                    secao_texto.append(f"    VSTR {reg_valor}, [R0]")
                else:
                    reg_carregado = f"D{cont_reg[0]}"
                    cont_reg[0] += 1
                    secao_texto.append(f"    LDR R0, ={nome_label}        @ load de {valor}")
                    secao_texto.append(f"    VLDR {reg_carregado}, [R0]")
                    pilha_regs.append(reg_carregado)

            # KEYWORD_RES: acessa histórico de resultados
            elif tipo == "KEYWORD_RES":
                if len(pilha_regs) < 1:
                    secao_texto.append(f"    @ ERRO: falta N para RES")
                    continue
                
                reg_n = pilha_regs.pop()
                reg_res = f"D{cont_reg[0]}"
                cont_reg[0] += 1
                
                secao_texto.append(f"    @ RES: acessa resultado anterior (total - N)")
                secao_texto.append(f"    VCVT.S32.F64 S31, {reg_n}")
                secao_texto.append(f"    VMOV R0, S31                @ R0 = N inteiro")
                secao_texto.append(f"    LDR R1, =resultados")
                secao_texto.append(f"    LDR R2, =numResultados")
                secao_texto.append(f"    LDR R2, [R2]                @ R2 = contador total")
                secao_texto.append(f"    SUB R2, R2, R0              @ indice = total - N")
                secao_texto.append(f"    LSL R2, R2, #3              @ offset em bytes (double = 8 bytes)")
                secao_texto.append(f"    ADD R1, R1, R2              @ R1 = endereço de resultados[indice]")
                secao_texto.append(f"    VLDR {reg_res}, [R1]        @ resgata o valor para {reg_res}")
                pilha_regs.append(reg_res)

        # Armazena resultado no histórico (se a pilha tiver exatamente 1 valor)
        if len(pilha_regs) == 1:
            reg_final = pilha_regs[0]
            secao_texto.append(f"    @ Armazena resultado no histórico")
            secao_texto.append(f"    LDR R0, =numResultados")
            secao_texto.append(f"    LDR R1, [R0]                @ R1 = numResultados atual")
            secao_texto.append(f"    LDR R2, =resultados")
            secao_texto.append(f"    LSL R3, R1, #3              @ offset = R1 * 8")
            secao_texto.append(f"    ADD R2, R2, R3")
            secao_texto.append(f"    VSTR {reg_final}, [R2]               @ guarda resultado")
            secao_texto.append(f"    ADD R1, R1, #1")
            secao_texto.append(f"    STR R1, [R0]                @ numResultados++")

        return pilha_regs[0] if pilha_regs else None


    def percorrerArvore(no):
        """Percorre a árvore buscando nós 'comando' no nível do comando_lista."""
        if "nodo_pai" in no:
            nome = no["nodo_pai"]

            if nome == "comando":
                processarComando(no)
                return
            elif nome == "comando_descartado":
                secao_texto.append("")
                secao_texto.append(f"    @ AVISO: Uma linha inteira foi ignorada pelo compilador. Motivo: {no.get('motivo', 'Desconhecido')}")
                return

        # Se não é um comando, continua descendo na árvore
        if "nodos_filhos" in no:
            for filho in no["nodos_filhos"]:
                percorrerArvore(filho)

    # Percorre a partir da raiz
    percorrerArvore(arvore)

    # Adiciona histórico de resultados ao .data
    secao_dados.append("    .align 3")
    secao_dados.append("    resultados: .space 800       @ espaço para 100 doubles")
    secao_dados.append("    numResultados: .word 0")

    codigo_final = []
    codigo_final.append(".global _start")
    codigo_final.append("")
    codigo_final.append(".data")
    codigo_final.extend(secao_dados)
    codigo_final.append("")
    codigo_final.append(".text")
    codigo_final.append("_start:")
    codigo_final.extend(secao_texto)
    codigo_final.append("")
    codigo_final.append("    @ Fim do programa")
    codigo_final.append("fim:")
    codigo_final.append("    B fim")

    # Salva o arquivo .s
    nome_saida = nome_arquivo.replace(".txt", ".s")
    try:
        with open(nome_saida, 'w', encoding='utf-8') as f:
            for linha in codigo_final:
                f.write(linha + "\n")
        print(f"Assembly gerado e salvo em '{nome_saida}'.")
    except Exception as e:
        print(f"Erro ao salvar Assembly: {e}")

    return codigo_final

def main():
    if len(sys.argv) < 2:
        print("Uso: python sintatico.py <arquivo_teste>")
        return

    # Arquivo teste passado via terminal
    arquivo_codigo_fonte = sys.argv[1]

    linhas_brutas = []
    lerArquivo(arquivo_codigo_fonte, linhas_brutas)

    # Temos que gerar os tokens.txt a partir do arquivo teste passado via terminal do sintático
    gerarTokens(linhas_brutas) # gera o tokens.txt usando parseExpressao do léxico

    arquivo_tokens = 'tokens.txt' # nome fixo do arquivo de tokens gerado pela função acima
    tokens = lerTokens(arquivo_tokens)

    # Testes para debug dos tokens lidos
    print(f"Foram lidas {len(tokens)} linhas de código válidas.\n")

    resultado_gramatica = construirGramatica()

    exibirGramatica(resultado_gramatica)
    print("\n        INÍCIO DO PROCESSADOR SINTÁTICO DA FITA        \n")
       
    # Aciona o analisador repassando o buffer extraído e a tabela formatada
    derivacao = parsear(tokens, resultado_gramatica["tabela_ll1"])

    # Gera o arquivo arvore_sintatica.md e arvore_sintatica.json
    arvore = gerarArvore(derivacao, arquivo_codigo_fonte)

    if arvore is not None:
        gerarAssembly(arvore, arquivo_codigo_fonte)
    else:
        print("Erro: A árvore não foi gerada corretamente. Geração de Assembly abortada.")

if __name__ == "__main__":
    main()