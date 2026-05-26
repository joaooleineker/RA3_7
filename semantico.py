# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

import sys
import json

from lexico import lerArquivo
from sintatico import construirGramatica, gerarTokens, lerTokens, parsear, gerarArvore, coletarTerminais

class EntradaTabelaSimbolos:
    """Representa uma entrada individual na tabela de símbolos."""
    def __init__(self, nome, tipo, linha_definicao, escopo="global"):
        self.nome = nome                        
        self.tipo = tipo                        
        self.linha_definicao = linha_definicao  
        self.linha_ultimo_uso = linha_definicao 
        self.escopo = escopo                    

class TabelaSimbolos:
    """Gerencia o dicionário de símbolos do programa."""
    def __init__(self):
        self.simbolos = {} 

    def definir(self, nome, tipo, linha):
        self.simbolos[nome] = EntradaTabelaSimbolos(nome, tipo, linha)

    def buscar(self, nome):
        return self.simbolos.get(nome, None)

    def atualizarUso(self, nome, linha):
        if nome in self.simbolos:
            self.simbolos[nome].linha_ultimo_uso = linha

def decorarArvoreComLinhas(arvore, tokens):
    """
    Decora os nós terminais da AST com o número de linha original.
    Percorre a árvore em pré-ordem e a fita flat de tokens em paralelo,
    injetando o atributo 'linha' em cada nó terminal (exceto ε).
    """

    flat_tokens = []
    for linha_tokens in tokens:
        for token in linha_tokens:
            flat_tokens.append(token)

    indice = [0] 

    def percorrer(no):
        if not isinstance(no, dict):
            return

        if "terminal_folha" in no:
            if no["terminal_folha"] != "ε":
                if indice[0] < len(flat_tokens):
                    no["linha"] = flat_tokens[indice[0]].linha
                    indice[0] += 1
                else:
                    no["linha"] = -1
            else:
                no["linha"] = -1
        elif "nodos_filhos" in no:
            for filho in no["nodos_filhos"]:
                percorrer(filho)

    percorrer(arvore)


def inferirTipoNumero(valor_texto):
    if "." in valor_texto:
        return "real"
    return "inteiro"


def inferirTipoOperacao(operador, tipo_a, tipo_b):
    if operador in ("/", "%"):
        return "inteiro"
    elif operador == "|":
        return "real"
    elif operador in ("+", "-", "*", "^"):
        if tipo_a == "inteiro" and tipo_b == "inteiro":
            return "inteiro"
        return "real"
    return "real"


def extrairComandosTopLevel(arvore):
    comandos = []

    def percorrerLista(no):
        if not isinstance(no, dict):
            return
        nome_no = no.get("nodo_pai", "")
        if nome_no == "comando_lista":
            for filho in no.get("nodos_filhos", []):
                if isinstance(filho, dict):
                    if filho.get("nodo_pai") == "comando":
                        comandos.append(filho)
                    elif filho.get("nodo_pai") == "comando_lista":
                        percorrerLista(filho)
        elif nome_no == "programa":
            for filho in no.get("nodos_filhos", []):
                percorrerLista(filho)

    percorrerLista(arvore)
    return comandos


def detectarTipoComando(no_conteudo):
    producao = no_conteudo.get("producao_acionada", "")

    if producao == "KEYWORD_START":
        return "start"
    if producao == "KEYWORD_END":
        return "end"

    # Para WHILE e IF, a produção é "comando sufixo_comando"
    # Precisamos verificar se sufixo_comando contém apos_cmd com WHILE ou IF
    if not producao.startswith("comando"):
        return "regular"

    # Busca o nó sufixo_comando entre os filhos
    sufixo_cmd = None
    for filho in no_conteudo.get("nodos_filhos", []):
        if isinstance(filho, dict) and filho.get("nodo_pai") == "sufixo_comando":
            sufixo_cmd = filho
            break

    if sufixo_cmd is None:
        return "regular"

    # Verifica se sufixo_comando contém apos_cmd
    apos_cmd = None
    for filho in sufixo_cmd.get("nodos_filhos", []):
        if isinstance(filho, dict) and filho.get("nodo_pai") == "apos_cmd":
            apos_cmd = filho
            break

    if apos_cmd is None:
        return "regular"

    # Verifica a produção de apos_cmd
    producao_apos = apos_cmd.get("producao_acionada", "")

    if producao_apos == "KEYWORD_WHILE":
        return "while"
    if producao_apos == "comando KEYWORD_IF":
        return "if"

    return "regular"

def processarComandoSemantico(no_comando, tabela, erros, historico_resultados, registrar_historico=True):
    """
    Processa um nó 'comando' da AST, atualizando a tabela de símbolos
    e registrando erros semânticos de declaração.
    """
    filhos = no_comando.get("nodos_filhos", [])
    no_conteudo = None
    for filho in filhos:
        if isinstance(filho, dict) and filho.get("nodo_pai") == "conteudo_comando":
            no_conteudo = filho
            break

    if no_conteudo is None:
        return None

    tipo_comando = detectarTipoComando(no_conteudo)

    # START e END não produzem resultado
    if tipo_comando in ("start", "end"):
        return None

    # WHILE: processa condição e corpo recursivamente
    if tipo_comando == "while":
        processarWhile(no_conteudo, tabela, erros, historico_resultados)
        return None

    # IF: processa condição, then e else recursivamente
    if tipo_comando == "if":
        processarIf(no_conteudo, tabela, erros, historico_resultados)
        return None

    # Comando regular: simula pilha RPN com os terminais
    terminais = coletarTerminais(no_conteudo)
    tipo_resultado = processarComandoRegular(terminais, tabela, erros, historico_resultados)

    if tipo_resultado is not None and registrar_historico:
        historico_resultados.append(tipo_resultado)

    return tipo_resultado


def processarWhile(no_conteudo, tabela, erros, historico_resultados):
    """
    Processa a estrutura semântica de um comando WHILE.
    """
    filhos = no_conteudo.get("nodos_filhos", [])
    cmd_condicao = None
    sufixo_cmd = None

    for filho in filhos:
        if isinstance(filho, dict):
            if filho.get("nodo_pai") == "comando" and cmd_condicao is None:
                cmd_condicao = filho
            elif filho.get("nodo_pai") == "sufixo_comando":
                sufixo_cmd = filho

    # Extrai o comando do corpo (primeiro 'comando' dentro de sufixo_comando)
    cmd_corpo = None
    if sufixo_cmd:
        for filho in sufixo_cmd.get("nodos_filhos", []):
            if isinstance(filho, dict) and filho.get("nodo_pai") == "comando":
                cmd_corpo = filho
                break

    # Processa a condição (registrar_historico=False pois sub-comandos de controle
    # não contribuem ao histórico de resultados do programa)
    if cmd_condicao:
        processarComandoSemantico(cmd_condicao, tabela, erros, historico_resultados, registrar_historico=False)

    # Processa o corpo
    if cmd_corpo:
        processarComandoSemantico(cmd_corpo, tabela, erros, historico_resultados, registrar_historico=False)


def processarIf(no_conteudo, tabela, erros, historico_resultados):
    """
    Processa a estrutura semântica de um comando IF.
    """
    filhos = no_conteudo.get("nodos_filhos", [])
    cmd_condicao = None
    sufixo_cmd = None

    for filho in filhos:
        if isinstance(filho, dict):
            if filho.get("nodo_pai") == "comando" and cmd_condicao is None:
                cmd_condicao = filho
            elif filho.get("nodo_pai") == "sufixo_comando":
                sufixo_cmd = filho

    # Extrai then e apos_cmd de sufixo_comando
    cmd_then = None
    apos_cmd = None
    if sufixo_cmd:
        for filho in sufixo_cmd.get("nodos_filhos", []):
            if isinstance(filho, dict):
                if filho.get("nodo_pai") == "comando":
                    cmd_then = filho
                elif filho.get("nodo_pai") == "apos_cmd":
                    apos_cmd = filho

    # Extrai else de apos_cmd
    cmd_else = None
    if apos_cmd:
        for filho in apos_cmd.get("nodos_filhos", []):
            if isinstance(filho, dict) and filho.get("nodo_pai") == "comando":
                cmd_else = filho

    # Processa condição
    if cmd_condicao:
        processarComandoSemantico(cmd_condicao, tabela, erros, historico_resultados, registrar_historico=False)

    # Processa bloco then
    if cmd_then:
        processarComandoSemantico(cmd_then, tabela, erros, historico_resultados, registrar_historico=False)

    # Processa bloco else
    if cmd_else:
        processarComandoSemantico(cmd_else, tabela, erros, historico_resultados, registrar_historico=False)


def processarComandoRegular(terminais, tabela, erros, historico_resultados):
    """
    Simula a pilha RPN para um comando regular (não WHILE/IF).
    Cada elemento da pilha é uma tupla (tipo, valor_literal_ou_None).
    Determina se cada MEMORIA é um LOAD ou STORE pela lógica RPN:
    """
    pilha = []  

    for terminal in terminais:
        tipo_terminal = terminal.get("terminal_folha", "")
        valor = terminal.get("valor_extraido", "")
        linha = terminal.get("linha", -1)

        if tipo_terminal in ("ABRE_PAREN", "FECHA_PAREN", "ε"):
            continue

        if tipo_terminal == "NUMERO":
            tipo_num = inferirTipoNumero(valor)
            try:
                valor_numerico = float(valor)
            except ValueError:
                valor_numerico = None
            pilha.append((tipo_num, valor_numerico))

        elif tipo_terminal == "OPERADOR":
            if len(pilha) >= 2:
                tipo_b, _ = pilha.pop()
                tipo_a, _ = pilha.pop()
                tipo_res = inferirTipoOperacao(valor, tipo_a, tipo_b)
                pilha.append((tipo_res, None))

        elif tipo_terminal == "OPERADOR_REL":
            if len(pilha) >= 2:
                pilha.pop()
                pilha.pop()
                pilha.append(("bool", None))

        elif tipo_terminal == "MEMORIA":
            if len(pilha) > 0:
                tipo_valor, _ = pilha.pop()
                entrada_existente = tabela.buscar(valor)

                if entrada_existente is None:
                    tabela.definir(valor, tipo_valor, linha)
                else:
                    if entrada_existente.tipo != tipo_valor:
                        erros.append({
                            "linha": linha,
                            "variavel": valor,
                            "mensagem": f"Redefinição incompatível da variável '{valor}' — tipo existente: {entrada_existente.tipo}, tipo atribuído: {tipo_valor}."
                        })
                    tabela.atualizarUso(valor, linha)
            else:
                entrada_existente = tabela.buscar(valor)

                if entrada_existente is None:
                    erros.append({
                        "linha": linha,
                        "variavel": valor,
                        "mensagem": f"Variável '{valor}' usada antes de ser definida."
                    })
                    pilha.append(("real", None))
                else:
                    pilha.append((entrada_existente.tipo, None))
                    tabela.atualizarUso(valor, linha)

        elif tipo_terminal == "KEYWORD_RES":
            if len(pilha) >= 1:
                tipo_n, valor_n = pilha.pop()

                if tipo_n != "inteiro":
                    erros.append({
                        "linha": linha,
                        "variavel": None,
                        "mensagem": f"Argumento de RES deve ser do tipo 'inteiro', mas recebeu '{tipo_n}'."
                    })

                tipo_resultado_res = "real"

                if valor_n is not None:
                    n_int = int(valor_n)
                    if n_int <= 0:
                        erros.append({
                            "linha": linha,
                            "variavel": None,
                            "mensagem": f"RES({n_int}) inválido — N deve ser um inteiro positivo."
                        })
                    elif n_int > len(historico_resultados):
                        erros.append({
                            "linha": linha,
                            "variavel": None,
                            "mensagem": f"RES({n_int}) fora do alcance — apenas {len(historico_resultados)} resultado(s) disponível(is) no histórico."
                        })
                    else:
                        tipo_resultado_res = historico_resultados[len(historico_resultados) - n_int]

                pilha.append((tipo_resultado_res, None))
            else:
                erros.append({
                    "linha": linha,
                    "variavel": None,
                    "mensagem": "Argumento faltando para RES."
                })

    # Resultado do comando: se exatamente 1 valor na pilha, o comando produz resultado
    if len(pilha) == 1:
        tipo_resultado, _ = pilha[0]
        return tipo_resultado

    return None

def construirTabelaSimbolos(arvore_sintatica):
    """
    Percorre a árvore sintática e constrói a tabela de símbolos,
    registrando variáveis, tipos inferidos, linhas de declaração e uso.
    Também valida declarações e referências a RES.
    Fornece a tabela de símbolos para verificarTipos() e gerarArvoreAtribuida().
    """
    tabela = TabelaSimbolos()
    erros = []
    historico_resultados = []  

    # Extrai os comandos de nível superior (dentro de comando_lista)
    comandos = extrairComandosTopLevel(arvore_sintatica)

    # Processa cada comando sequencialmente
    for cmd in comandos:
        processarComandoSemantico(cmd, tabela, erros, historico_resultados, registrar_historico=True)

    # Salva artefatos em arquivos Markdown
    salvarTabelaSimbolos(tabela)
    salvarErrosSemanticos(erros)

    return tabela, erros

def salvarTabelaSimbolos(tabela, nome_arquivo="tabela_simbolos.md"):
    """Salva a tabela de símbolos em formato Markdown."""
    linhas = []
    linhas.append("# Tabela de Símbolos\n")
    linhas.append("| Nome            | Tipo     | Escopo | Linha Definição | Linha Último Uso |")
    linhas.append("|-----------------|----------|--------|-----------------|------------------|")

    if tabela.simbolos:
        for nome in sorted(tabela.simbolos.keys()):
            entrada = tabela.simbolos[nome]
            linhas.append(
                f"| {entrada.nome:<15} | {entrada.tipo:<8} | {entrada.escopo:<6} "
                f"| {str(entrada.linha_definicao):<15} | {str(entrada.linha_ultimo_uso):<16} |"
            )
    else:
        linhas.append("| _(nenhuma variável registrada)_ | - | - | - | - |")

    linhas.append("")

    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_tabela:
            arquivo_tabela.write("\n".join(linhas) + "\n")
        print(f"Tabela de símbolos salva em '{nome_arquivo}'.")
    except Exception as e:
        print(f"Erro ao salvar tabela de símbolos: {e}")


def salvarErrosSemanticos(erros, nome_arquivo="erros_semanticos.md"):
    """Salva a lista de erros semânticos em formato Markdown."""
    linhas = []
    linhas.append("# Relatório de Erros Semânticos\n")

    if not erros:
        linhas.append("Nenhum erro semântico encontrado.\n")
    else:
        linhas.append(f"Total de erros encontrados: **{len(erros)}**\n")

        for indice_erro, erro in enumerate(erros, 1):
            linha_erro = erro.get("linha", "?")
            variavel = erro.get("variavel", None)
            mensagem = erro.get("mensagem", "Erro desconhecido.")

            linhas.append(f"### Erro {indice_erro}")
            linhas.append(f"- **Linha:** {linha_erro}")
            if variavel:
                linhas.append(f"- **Variável:** {variavel}")
            linhas.append(f"- **Descrição:** {mensagem}")
            linhas.append("")

    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_erros:
            arquivo_erros.write("\n".join(linhas) + "\n")
        print(f"Relatório de erros semânticos salvo em '{nome_arquivo}'.")
    except Exception as e:
        print(f"Erro ao salvar relatório de erros: {e}")

def prepararEntradaSemantica(nome_arquivo):
    linhas_arquivo = []
    lerArquivo(nome_arquivo, linhas_arquivo)

    print("Arquivo carregado com sucesso.")
    print("Quantidade de linhas:", len(linhas_arquivo))

    # Utilizando as funções criadas no sintático
    gerarTokens(linhas_arquivo)
    tokens = lerTokens("tokens.txt")

    # Valida se o programa começa com (START) e termina com (END)
    erros = validarInicioFimPrograma(tokens)
    if len(erros) > 0:
        for erro in erros:
            print(erro)

        return tokens, None

    resultado_gramatica = construirGramatica()
    derivacao = parsear(tokens, resultado_gramatica["tabela_ll1"])
    arvore_sintatica_inicial = gerarArvore(derivacao, nome_arquivo)

    return tokens, arvore_sintatica_inicial

def validarInicioFimPrograma(tokens):
    erros = []

    if len(tokens) == 0:
        erros.append("Erro: programa vazio.")
        return erros

    primeira_linha = tokens[0]
    ultima_linha = tokens[-1]

    inicio_valido = (
        len(primeira_linha) == 3
        and primeira_linha[0].tipo == "ABRE_PAREN"
        and primeira_linha[1].tipo == "KEYWORD_START"
        and primeira_linha[2].tipo == "FECHA_PAREN"
    )

    fim_valido = (
        len(ultima_linha) == 3
        and ultima_linha[0].tipo == "ABRE_PAREN"
        and ultima_linha[1].tipo == "KEYWORD_END"
        and ultima_linha[2].tipo == "FECHA_PAREN"
    )

    if not inicio_valido:
        erros.append("Erro: o programa deve comecar com (START).")

    if not fim_valido:
        erros.append("Erro: o programa deve terminar com (END).")

    return erros

def verificarTipos(arvore_sintatica, tabela_simbolos):
    """
    Valida os tipos das expressões, comandos especiais, decisões e laços.
    Anota os nós terminais da árvore com 'tipo_inferido' e nós de conteudo_comando
    com 'tipo_resultado'.

    Entrada: árvore sintática inicial e tabela de símbolos (já construída)
    Saída: lista de erros semânticos de tipo
    Fornece informações de tipo para gerarArvoreAtribuida().
    """
    erros_tipo = []
    historico_tipos = []  # tipos dos resultados produzidos (para RES)

    comandos = extrairComandosTopLevel(arvore_sintatica)

    for cmd in comandos:
        # Verifica a validade dos tipos de cada comando na arvore sintatica
        auxChecarTiposComando(cmd, tabela_simbolos, erros_tipo, historico_tipos, registrar_historico=True)

    # Exporta os erros semanticos encontrados para o arquivo Markdown
    auxSalvarRelatorioTipos(erros_tipo)

    return erros_tipo


def auxChecarTiposComando(no_comando, tabela, erros, historico, registrar_historico=True):
    """
    Despacha a verificação de tipos para o tipo correto de comando
    (START/END, WHILE, IF ou regular).
    """
    filhos = no_comando.get("nodos_filhos", [])
    no_conteudo = None
    for filho in filhos:
        if isinstance(filho, dict) and filho.get("nodo_pai") == "conteudo_comando":
            no_conteudo = filho
            break

    if no_conteudo is None:
        return None

    tipo_cmd = detectarTipoComando(no_conteudo)

    # START e END não produzem resultado
    if tipo_cmd in ("start", "end"):
        return None

    if tipo_cmd == "while":
        auxChecarTiposWhile(no_conteudo, tabela, erros, historico)
        return None

    if tipo_cmd == "if":
        auxChecarTiposIf(no_conteudo, tabela, erros, historico)
        return None

    # Comando regular: simula a pilha RPN com verificação estrita
    terminais = coletarTerminais(no_conteudo)
    tipo_resultado = auxChecarTiposRegular(terminais, tabela, erros, historico)

    if tipo_resultado is not None:
        no_conteudo["tipo_resultado"] = tipo_resultado  # anotação na árvore
        if registrar_historico:
            historico.append(tipo_resultado)

    return tipo_resultado


def auxChecarTiposWhile(no_conteudo, tabela, erros, historico):
    """
    Verifica tipos do WHILE: a condição deve produzir 'bool'.
    O corpo é processado mas não registra no histórico global.
    """
    filhos = no_conteudo.get("nodos_filhos", [])
    cmd_condicao = None
    sufixo_cmd = None

    for filho in filhos:
        if isinstance(filho, dict):
            if filho.get("nodo_pai") == "comando" and cmd_condicao is None:
                cmd_condicao = filho
            elif filho.get("nodo_pai") == "sufixo_comando":
                sufixo_cmd = filho

    # Extrai o comando do corpo dentro de sufixo_comando
    cmd_corpo = None
    if sufixo_cmd:
        for filho in sufixo_cmd.get("nodos_filhos", []):
            if isinstance(filho, dict) and filho.get("nodo_pai") == "comando":
                cmd_corpo = filho
                break

    # Verifica se a condição produz bool
    if cmd_condicao:
        # Avalia a condicao do WHILE e pega o seu tipo de retorno (esperado: bool)
        tipo_cond = auxChecarTiposComando(cmd_condicao, tabela, erros, historico, registrar_historico=False)
        
        if tipo_cond is not None:
            tipo_desc = tipo_cond
        else:
            tipo_desc = "nenhum valor produzido"

        if tipo_cond != "bool":
            terminais_cond = coletarTerminais(cmd_condicao)
            linha_cond = terminais_cond[0].get("linha", -1) if terminais_cond else -1
            erros.append({
                "linha": linha_cond,
                "variavel": None,
                "mensagem": (
                    f"Condição do WHILE deve ser do tipo 'bool', "
                    f"mas é '{tipo_desc}'."
                )
            })

    # Processa o corpo sem registrar no histórico global
    if cmd_corpo:
        auxChecarTiposComando(cmd_corpo, tabela, erros, historico, registrar_historico=False)


def auxChecarTiposIf(no_conteudo, tabela, erros, historico):
    """
    Verifica tipos do IF: a condição deve produzir 'bool'.
    Os blocos then e else são processados mas não registram no histórico global.
    """
    filhos = no_conteudo.get("nodos_filhos", [])
    cmd_condicao = None
    sufixo_cmd = None

    for filho in filhos:
        if isinstance(filho, dict):
            if filho.get("nodo_pai") == "comando" and cmd_condicao is None:
                cmd_condicao = filho
            elif filho.get("nodo_pai") == "sufixo_comando":
                sufixo_cmd = filho

    # Extrai then e apos_cmd de sufixo_comando
    cmd_then = None
    apos_cmd = None
    if sufixo_cmd:
        for filho in sufixo_cmd.get("nodos_filhos", []):
            if isinstance(filho, dict):
                if filho.get("nodo_pai") == "comando":
                    cmd_then = filho
                elif filho.get("nodo_pai") == "apos_cmd":
                    apos_cmd = filho

    # Extrai else de apos_cmd
    cmd_else = None
    if apos_cmd:
        for filho in apos_cmd.get("nodos_filhos", []):
            if isinstance(filho, dict) and filho.get("nodo_pai") == "comando":
                cmd_else = filho

    # Verifica se a condição produz bool
    if cmd_condicao:
        # Avalia a condicao do IF e pega o seu tipo de retorno (esperado: bool)
        tipo_cond = auxChecarTiposComando(cmd_condicao, tabela, erros, historico, registrar_historico=False)
        
        if tipo_cond is not None:
            tipo_desc = tipo_cond
        else:
            tipo_desc = "nenhum valor produzido"

        if tipo_cond != "bool":
            terminais_cond = coletarTerminais(cmd_condicao)
            linha_cond = terminais_cond[0].get("linha", -1) if terminais_cond else -1
            erros.append({
                "linha": linha_cond,
                "variavel": None,
                "mensagem": (
                    f"Condição do IF deve ser do tipo 'bool', "
                    f"mas é '{tipo_desc}'."
                )
            })

    # Processa then e else sem registrar no histórico global
    if cmd_then:
        auxChecarTiposComando(cmd_then, tabela, erros, historico, registrar_historico=False)
    if cmd_else:
        auxChecarTiposComando(cmd_else, tabela, erros, historico, registrar_historico=False)


def auxChecarTiposRegular(terminais, tabela, erros, historico):
    """
    Simula a pilha RPN com verificação estrita de tipos.
    Anota cada terminal com 'tipo_inferido'.

    Regras de compatibilidade:
      - bool NAO pode ser operando de operadores aritméticos
      - '/' e '%' exigem ambos os operandos como 'inteiro'
      - '|' produz sempre 'real'; operandos devem ser numéricos
      - '+', '-', '*', '^' aceitam int/real; int+int->int, qualquer real->real
      - Operadores relacionais produzem 'bool'
      - '<', '>', '<=', '>=' nao aceitam bool como operando
      - '==' e '!=' aceitam bool (mas ambos os operandos devem ter o mesmo tipo)
    """
    tipos_numericos = {"inteiro", "real"}  # tipos aceitos em operações aritméticas

    # Pilha de tuplas: (tipo, valor_numerico_ou_None)
    pilha = []

    for terminal in terminais:
        tipo_token = terminal.get("terminal_folha", "")
        valor = terminal.get("valor_extraido", "")
        linha = terminal.get("linha", -1)

        if tipo_token in ("ABRE_PAREN", "FECHA_PAREN", "ε"):
            continue

        # NUMERO: inteiro se não contém ponto, real caso contrário
        if tipo_token == "NUMERO":
            if "." in valor:
                tipo_inferido = "real"
            else:
                tipo_inferido = "inteiro"
                
            terminal["tipo_inferido"] = tipo_inferido
            try:
                valor_num = float(valor)
            except ValueError:
                valor_num = None
            pilha.append((tipo_inferido, valor_num))

        # OPERADOR aritmetico
        elif tipo_token == "OPERADOR":
            if len(pilha) < 2:
                terminal["tipo_inferido"] = "real"  # recuperação
                pilha.append(("real", None))
                continue

            tipo_b, _ = pilha.pop()
            tipo_a, _ = pilha.pop()

            # Bool nao pode participar de operações aritméticas
            if tipo_a == "bool" or tipo_b == "bool":
                erros.append({
                    "linha": linha,
                    "variavel": None,
                    "mensagem": (
                        f"Operador '{valor}' nao pode ser aplicado ao tipo 'bool'. "
                        f"Operandos encontrados: '{tipo_a}' e '{tipo_b}'."
                    )
                })
                terminal["tipo_inferido"] = "real"  # recuperação
                pilha.append(("real", None))
                continue

            # Divisão inteira e resto: ambos os operandos devem ser 'inteiro'
            if valor in ("/", "%"):
                if tipo_a != "inteiro" or tipo_b != "inteiro":
                    erros.append({
                        "linha": linha,
                        "variavel": None,
                        "mensagem": (
                            f"Operador '{valor}' requer operandos do tipo 'inteiro', "
                            f"mas recebeu '{tipo_a}' e '{tipo_b}'."
                        )
                    })
                tipo_resultado = "inteiro"

            # Divisão real: operandos numéricos, resultado sempre 'real'
            elif valor == "|":
                tipo_resultado = "real"

            # Soma, subtração, multiplicação e potenciação: int+int->int, qualquer real->real
            else:  # +, -, *, ^
                if tipo_a == "inteiro" and tipo_b == "inteiro":
                    tipo_resultado = "inteiro"
                else:
                    tipo_resultado = "real"

            terminal["tipo_inferido"] = tipo_resultado
            pilha.append((tipo_resultado, None))

        # OPERADOR relacional: sempre produz 'bool'
        elif tipo_token == "OPERADOR_REL":
            if len(pilha) < 2:
                terminal["tipo_inferido"] = "bool"  # recuperação
                pilha.append(("bool", None))
                continue

            tipo_b, _ = pilha.pop()
            tipo_a, _ = pilha.pop()

            # Bool so pode ser comparado com == e !=
            if (tipo_a == "bool" or tipo_b == "bool") and valor not in ("==", "!="):
                erros.append({
                    "linha": linha,
                    "variavel": None,
                    "mensagem": (
                        f"Operador relacional '{valor}' nao pode ser aplicado ao tipo 'bool'. "
                        f"Apenas '==' e '!=' sao permitidos com booleanos."
                    )
                })

            # Tipos incompatíveis entre si (ex: bool vs inteiro)
            if tipo_a != tipo_b and not (tipo_a in tipos_numericos and tipo_b in tipos_numericos):
                erros.append({
                    "linha": linha,
                    "variavel": None,
                    "mensagem": (
                        f"Comparacao entre tipos incompatíveis: '{tipo_a}' e '{tipo_b}'."
                    )
                })

            terminal["tipo_inferido"] = "bool"
            pilha.append(("bool", None))

        # MEMORIA: STORE (pilha tem valor) ou LOAD (pilha vazia)
        elif tipo_token == "MEMORIA":
            entrada = tabela.buscar(valor)

            if len(pilha) > 0:
                # STORE: consome o topo da pilha e anota com o tipo armazenado
                tipo_valor, _ = pilha.pop()
                terminal["tipo_inferido"] = tipo_valor
            else:
                # LOAD: recupera o tipo da tabela de símbolos
                if entrada is not None:
                    tipo_mem = entrada.tipo
                else:
                    tipo_mem = "real"  # recuperação
                
                terminal["tipo_inferido"] = tipo_mem
                pilha.append((tipo_mem, None))

        # KEYWORD_RES: tipo do resultado referenciado
        elif tipo_token == "KEYWORD_RES":
            if len(pilha) >= 1:
                tipo_n, valor_n = pilha.pop()

                tipo_resultado_res = "real"  # padrão de recuperação
                if valor_n is not None:
                    n_int = int(valor_n)
                    if 1 <= n_int <= len(historico):
                        tipo_resultado_res = historico[len(historico) - n_int]

                terminal["tipo_inferido"] = tipo_resultado_res
                pilha.append((tipo_resultado_res, None))

    # O resultado do comando é o único valor que sobrou na pilha
    if len(pilha) == 1:
        tipo_final, _ = pilha[0]
        return tipo_final

    return None


def auxSalvarRelatorioTipos(erros_tipo, nome_arquivo="relatorio_tipos.md"):
    """Salva o relatório de erros semânticos de tipo em formato Markdown."""
    linhas = ["# Relatorio de Verificacao de Tipos\n"]

    if not erros_tipo:
        linhas.append("Nenhum erro de tipo encontrado.\n")
    else:
        linhas.append(f"Total de erros de tipo: **{len(erros_tipo)}**\n")

        for indice, erro in enumerate(erros_tipo, 1):
            linha_erro = erro.get("linha", "?")
            mensagem = erro.get("mensagem", "Erro desconhecido.")

            linhas.append(f"### Erro de Tipo {indice}")
            linhas.append(f"- **Linha:** {linha_erro}")
            linhas.append(f"- **Descricao:** {mensagem}")
            linhas.append("")

    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo_saida:
            arquivo_saida.write("\n".join(linhas) + "\n")
        print(f"Relatório de verificação de tipos salvo em '{nome_arquivo}'.")
    except Exception as erro_io:
        print(f"Erro ao salvar relatorio de tipos: {erro_io}")


def gerarArvoreAtribuida(arvore_sintatica, tabela_simbolos):
    pass

def gerarAssembly(arvore_atribuida):
    pass

def possuiErroLexico(tokens):
    for linha_tokens in tokens:
        for token in linha_tokens:
            if token.tipo == "ERRO" or token.tipo == "LINHA_INVALIDA":
                return True

    return False

def possuiErroSintatico(no):
    # Caso não exista árvore
    if no is None:
        return True

    if not isinstance(no, dict):
        return False

    # Procura erros na árvore
    if (
        no.get("nodo_pai") == "comando_descartado"
        or "erro" in no
        or "erro_sintatico" in no
        or "erro_nodo_pai" in no
    ):
        return True

    for filho in no.get("nodos_filhos", []):
        if possuiErroSintatico(filho):
            return True

    return False

def executarAnaliseSemantica(nome_arquivo):
    print(f"\n{'='*60}")
    print(f"ARQUIVO ANALISADO: {nome_arquivo}")
    print(f"{'='*60}\n")

    tokens, arvore_sintatica_inicial = prepararEntradaSemantica(nome_arquivo)

    # Reportar erros léxicos antes da etapa semântica
    if possuiErroLexico(tokens):
        print("Análise semântica interrompida: foram encontrados erros léxicos.")
        return

    # Reportar erros sintáticos antes da etapa semântica
    if possuiErroSintatico(arvore_sintatica_inicial):
        print("Análise semântica interrompida: foram encontrados erros sintáticos.")
        return

    decorarArvoreComLinhas(arvore_sintatica_inicial, tokens)

    # Aluno 2: constrói a tabela de símbolos e valida declarações
    tabela_simbolos, erros_declaracao = construirTabelaSimbolos(arvore_sintatica_inicial)

    print(f"\n{'='*60}")
    print("TABELA DE SÍMBOLOS")
    print(f"{'='*60}")
    if tabela_simbolos.simbolos:
        print(f"  {'Nome':<15} | {'Tipo':<8} | {'Definição':<10} | {'Último Uso':<10} | {'Escopo'}")
        print(f"  {'-'*15}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}")
        for nome_var in sorted(tabela_simbolos.simbolos.keys()):
            entrada = tabela_simbolos.simbolos[nome_var]
            print(
                f"  {entrada.nome:<15} | {entrada.tipo:<8} | "
                f"linha {entrada.linha_definicao:<4} | linha {entrada.linha_ultimo_uso:<4} | {entrada.escopo}"
            )
    else:
        print("  (nenhuma variável registrada)")
    print()

    # Aluno 3: verifica compatibilidade de tipos nas expressões
    erros_tipo = verificarTipos(arvore_sintatica_inicial, tabela_simbolos)

    # Consolida todos os erros semânticos
    todos_erros = erros_declaracao + erros_tipo

    if todos_erros:
        print(f"{'='*60}")
        print(f"ERROS SEMÂNTICOS ENCONTRADOS: {len(todos_erros)}")
        print(f"{'='*60}")
        for erro in todos_erros:
            linha_err = erro.get("linha", "?")
            mensagem = erro.get("mensagem", "")
            print(f"  Erro semântico (linha {linha_err}): {mensagem}")
        print()
    else:
        print("Análise semântica concluída sem erros.\n")

    print(f"{'='*60}")
    print("ARQUIVOS DE SAÍDA GERADOS")
    print(f"{'='*60}")
    print("  - tabela_simbolos.md")
    print("  - erros_semanticos.md")
    print("  - relatorio_tipos.md")
    print("  - arvore_sintatica.md")
    print("  - arvore_sintatica.json")
    print(f"{'='*60}")
    print("Analisador semântico concluído.")

def main():
    if len(sys.argv) < 2:
        print("Uso: python semantico.py <arquivo_teste>")
        return

    nome_arquivo = sys.argv[1]
    executarAnaliseSemantica(nome_arquivo)

if __name__ == "__main__":
    main()
