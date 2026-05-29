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
    print(f"\n{'='*60}")
    print("ANÁLISE LÉXICA")
    print(f"{'='*60}\n")

    linhas_arquivo = []
    lerArquivo(nome_arquivo, linhas_arquivo)
    print("Arquivo carregado com sucesso.")
    print(f"Linhas de código: {len(linhas_arquivo)}")

    gerarTokens(linhas_arquivo)
    tokens = lerTokens("tokens.txt")

    total_tokens = sum(len(linha) for linha in tokens)
    erros_lexicos = [t for linha in tokens for t in linha if t.tipo in ("ERRO", "LINHA_INVALIDA")]

    if erros_lexicos:
        print(f"Tokens gerados: {total_tokens} ({len(erros_lexicos)} com erro léxico)")
        for t in erros_lexicos:
            print(f"  Erro léxico: token inválido '{t.valor}'")
        print("Resultado da análise léxica: FALHOU\n")
        print("Análise sintática não executada (erros léxicos impedem o parsing).")
        return tokens, None

    print(f"Tokens gerados: {total_tokens} — nenhum erro léxico encontrado.")
    print("Resultado da análise léxica: OK\n")

    # Valida se o programa começa com (START) e termina com (END)
    erros_estrutura = validarInicioFimPrograma(tokens)
    if erros_estrutura:
        for erro in erros_estrutura:
            print(erro)
        print("Análise sintática não executada (estrutura de programa inválida).")
        return tokens, None

    print(f"\n{'='*60}")
    print("ANÁLISE SINTÁTICA")
    print(f"{'='*60}\n")

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

def copiarArvore(nodo):
    """
    Realiza uma cópia profunda (deep copy) manual da árvore,
    evitando a necessidade de importar o módulo 'copy'.
    """
    if isinstance(nodo, dict):
        return {chave: copiarArvore(valor) for chave, valor in nodo.items()}
    elif isinstance(nodo, list):
        return [copiarArvore(item) for item in nodo]
    else:
        return nodo

def gerarArvoreAtribuida(arvore_sintatica, tabela_simbolos):
    """
    Percorre a árvore sintática e constrói a árvore sintática atribuída (aumentada),
    anotando cada nó relevante com tipo, categoria semântica e informação para Assembly.
    Fase final da análise semântica (Aluno 4).
    """
    arvore_atribuida = copiarArvore(arvore_sintatica)

    # Executa a decoração recursiva da árvore
    auxDecorarArvoreAtribuida(arvore_atribuida, tabela_simbolos)

    # Salva os artefatos nos arquivos Markdown e JSON
    salvarArvoreAtribuida(arvore_atribuida)

    return arvore_atribuida

def auxDecorarArvoreAtribuida(arvore, tabela):
    """
    Função auxiliar recursiva que percorre a árvore sintática decorando os nós
    com tipo, categoria_semantica e info_assembly.
    """
    if not isinstance(arvore, dict):
        return

    nome_nodo = arvore.get("nodo_pai", "")

    # Decora os nós que contêm comandos
    if nome_nodo == "conteudo_comando":
        tipo_cmd = detectarTipoComando(arvore)

        if tipo_cmd in ("start", "end"):
            arvore["tipo"] = "void"
            arvore["categoria_semantica"] = "controle"
            arvore["info_assembly"] = "NOP"
            for filho in arvore.get("nodos_filhos", []):
                if isinstance(filho, dict) and "terminal_folha" in filho:
                    filho["tipo"] = "void"
                    filho["categoria_semantica"] = "controle"
                    filho["info_assembly"] = "NOP"
            return

        if tipo_cmd in ("while", "if"):
            arvore["tipo"] = "void"
            arvore["categoria_semantica"] = "controle"
            arvore["info_assembly"] = "DESVIO_CONDICIONAL"
            # Processa sub-estruturas (condição, then, else) recursivamente
            for filho in arvore.get("nodos_filhos", []):
                auxDecorarArvoreAtribuida(filho, tabela)
            return

        # Para comandos regulares, simula a pilha RPN para inferir categorias e tipos precisos
        terminais = coletarTerminais(arvore)
        pilha = []

        for terminal in terminais:
            tipo_token = terminal.get("terminal_folha", "")
            valor = terminal.get("valor_extraido", "")

            if tipo_token in ("ABRE_PAREN", "FECHA_PAREN", "ε"):
                terminal["tipo"] = "void"
                terminal["categoria_semantica"] = "pontuacao"
                terminal["info_assembly"] = "NENHUM"
                continue

            if tipo_token == "NUMERO":
                tipo_inferido = "real" if "." in valor else "inteiro"
                terminal["tipo"] = tipo_inferido
                terminal["categoria_semantica"] = "literal"
                terminal["info_assembly"] = f"LDR R0, ={valor}"
                pilha.append(tipo_inferido)

            elif tipo_token == "OPERADOR":
                if len(pilha) >= 2:
                    tipo_b = pilha.pop()
                    tipo_a = pilha.pop()
                    tipo_res = inferirTipoOperacao(valor, tipo_a, tipo_b)
                else:
                    tipo_res = "real"
                terminal["tipo"] = tipo_res
                terminal["categoria_semantica"] = "operador_aritmetico"
                terminal["info_assembly"] = f"OP_ARITMETICA {valor}"
                pilha.append(tipo_res)

            elif tipo_token == "OPERADOR_REL":
                if len(pilha) >= 2:
                    pilha.pop()
                    pilha.pop()
                terminal["tipo"] = "bool"
                terminal["categoria_semantica"] = "operador_relacional"
                terminal["info_assembly"] = f"OP_RELACIONAL {valor}"
                pilha.append("bool")

            elif tipo_token == "MEMORIA":
                entrada = tabela.buscar(valor)
                if len(pilha) > 0:
                    # Caso de atribuição (STORE)
                    tipo_valor = pilha.pop()
                    terminal["tipo"] = tipo_valor
                    terminal["categoria_semantica"] = "var_store"
                    terminal["info_assembly"] = f"STR R0, [{valor}]"
                else:
                    # Caso de leitura (LOAD)
                    tipo_mem = entrada.tipo if entrada else "real"
                    terminal["tipo"] = tipo_mem
                    terminal["categoria_semantica"] = "var_load"
                    terminal["info_assembly"] = f"LDR R0, [{valor}]"
                    pilha.append(tipo_mem)

            elif tipo_token == "KEYWORD_RES":
                if len(pilha) >= 1:
                    pilha.pop()
                tipo_res = "real"
                terminal["tipo"] = tipo_res
                terminal["categoria_semantica"] = "historico_res"
                terminal["info_assembly"] = "LDR R0, [HISTORICO]"
                pilha.append(tipo_res)

        # Anota o próprio comando com o seu tipo resultante
        if len(pilha) == 1:
            arvore["tipo"] = pilha[0]
            arvore["categoria_semantica"] = "expressao"
        else:
            arvore["tipo"] = "void"
            arvore["categoria_semantica"] = "expressao"

    elif "nodos_filhos" in arvore:
        for filho in arvore["nodos_filhos"]:
            auxDecorarArvoreAtribuida(filho, tabela)

def salvarArvoreAtribuida(arvore_atribuida):
    """
    Exporta a árvore atribuída nos formatos JSON e Markdown.
    """
    import json

    nome_json = "arvore_atribuida.json"
    nome_md = "arvore_atribuida.md"

    try:
        # Salva o arquivo JSON
        with open(nome_json, "w", encoding="utf-8") as arquivo_json:
            json.dump(arvore_atribuida, arquivo_json, ensure_ascii=False, indent=4)
        print(f"Sucesso: Árvore atribuída exportada para '{nome_json}'.")

        # Salva o arquivo Markdown
        linhas_arvore = construirTextoArvoreAtribuida(arvore_atribuida)
        texto_final = "\n".join(linhas_arvore)

        with open(nome_md, "w", encoding="utf-8") as arquivo_md:
            arquivo_md.write("# Árvore Sintática Atribuída (Aumentada)\n\n")
            arquivo_md.write("```text\n")
            arquivo_md.write(texto_final + "\n")
            arquivo_md.write("```\n")
        print(f"Sucesso: Árvore atribuída exportada para '{nome_md}'.")

    except Exception as erro_io:
        print(f"Erro ao salvar arquivos da árvore atribuída: {erro_io}")

def construirTextoArvoreAtribuida(no, prefixo="", eh_ultimo=True, eh_raiz=True):
    """
    Percorre a árvore atribuída gerando sua representação em formato de árvore de texto,
    incluindo as anotações semânticas de tipo e categoria.
    """
    linhas = []

    if no.get("nodo_pai") == "comando_descartado":
        return []

    # Define o rótulo do nó com suas atribuições
    tipo = no.get("tipo")
    categoria = no.get("categoria_semantica")
    sufixo_atrib = f" [tipo: {tipo}, cat: {categoria}]" if tipo and categoria else ""

    if "terminal_folha" in no:
        valor = no.get("valor_extraido", "")
        texto_no = f"{no['terminal_folha']} ({valor}){sufixo_atrib}"
    elif "nodo_pai" in no:
        texto_no = f"{no['nodo_pai']}{sufixo_atrib}"
    elif "erro_sintatico" in no:
        texto_no = f"ERRO SINTÁTICO: {no['erro_sintatico']}"
    elif "erro_nodo_pai" in no:
        texto_no = f"FALHA NO NÓ: {no['erro_nodo_pai']} (Token inesperado: {no.get('falha_registro', '')})"
    else:
        texto_no = "Nó Desconhecido"

    if eh_raiz:
        linhas.append(texto_no)
        novo_prefixo = ""
    else:
        if eh_ultimo:
            marcador = "└── "
            novo_prefixo = prefixo + "    "
        else:
            marcador = "├── "
            novo_prefixo = prefixo + "│   "

        linhas.append(f"{prefixo}{marcador}{texto_no}")

    if "nodos_filhos" in no:
        filhos = no["nodos_filhos"]
    else:
        filhos = []

    total_filhos = len(filhos)

    for indice_filho in range(total_filhos):
        filho = filhos[indice_filho]
        ultimo_filho = (indice_filho == total_filhos - 1)
        linhas_filho = construirTextoArvoreAtribuida(filho, novo_prefixo, ultimo_filho, False)
        linhas.extend(linhas_filho)

    return linhas

def gerarAssembly(arvore_atribuida, nome_arquivo="saida.s"):
    """
    Gera código Assembly ARMv7 (VFP) para o ambiente Cpulator-ARMv7 DE1-SoC(v16.1)
    a partir da árvore sintática atribuída gerada pelo analisador semântico.
    """

    secao_dados = []
    secao_texto = []
    contador_label = [0]
    labels_memoria = set()
    constantes_usadas = {}
    # Contadores separados para registradores inteiros e de ponto flutuante
    contador_reg_int = [0]   # R5 em diante (R0-R4 reservados para uso auxiliar)
    contador_reg_fp = [0]    # D0 em diante

    def obterLabelUnico(prefixo):
        """Gera um label único para controle de fluxo."""
        label = f"{prefixo}_{contador_label[0]}"
        contador_label[0] += 1
        return label

    def obterRegInt():
        """Obtém o próximo registrador inteiro disponível (R5-R12)."""
        reg = f"R{5 + contador_reg_int[0]}"
        contador_reg_int[0] += 1
        return reg

    def obterRegFP():
        """Obtém o próximo registrador VFP double disponível (D0-D14)."""
        reg = f"D{contador_reg_fp[0]}"
        contador_reg_fp[0] += 1
        return reg

    def garantirConstanteDouble(valor_texto):
        """Registra uma constante double no .data e retorna o nome do label."""
        chave = f"dbl_{valor_texto}"
        if chave in constantes_usadas:
            return constantes_usadas[chave]
        nome_label = "const_" + valor_texto.replace(".", "_").replace("-", "neg")
        constantes_usadas[chave] = nome_label
        secao_dados.append("    .align 3")
        secao_dados.append(f"    {nome_label}: .double {valor_texto}")
        return nome_label

    def garantirConstanteInt(valor_texto):
        """Registra uma constante inteira no .data e retorna o nome do label."""
        chave = f"int_{valor_texto}"
        if chave in constantes_usadas:
            return constantes_usadas[chave]
        nome_label = "iconst_" + valor_texto.replace("-", "neg")
        constantes_usadas[chave] = nome_label
        secao_dados.append(f"    {nome_label}: .word {valor_texto}")
        return nome_label

    def garantirMemoria(nome_mem, tipo_mem):
        """Registra uma variável de memória no .data (8 bytes para double, 4 para inteiro)."""
        nome_label = "mem_" + nome_mem
        if nome_label not in labels_memoria:
            if tipo_mem == "real":
                secao_dados.append("    .align 3")
                secao_dados.append(f"    {nome_label}: .double 0.0")
            else:
                secao_dados.append(f"    .align 2")
                secao_dados.append(f"    {nome_label}: .word 0")
            labels_memoria.add(nome_label)
        return nome_label

    def processarComandoAssembly(no_comando):
        """
        Processa um nó 'comando' da árvore atribuída e gera o Assembly correspondente.
        Retorna uma tupla (registrador, tipo) com o resultado, ou None.
        """
        # Reseta contadores de registradores a cada comando independente
        # para evitar ultrapassar os limites do ARM (R0-R12) e VFP (D0-D15)
        contador_reg_int[0] = 0
        contador_reg_fp[0] = 0

        filhos = no_comando.get("nodos_filhos", [])
        no_conteudo = None
        for filho in filhos:
            if isinstance(filho, dict) and filho.get("nodo_pai") == "conteudo_comando":
                no_conteudo = filho
                break

        if no_conteudo is None:
            return None

        tipo_cmd = detectarTipoComando(no_conteudo)

        # START / END
        if tipo_cmd == "start":
            secao_texto.append("")
            secao_texto.append("    @ (START) - inicio do programa")
            return None

        if tipo_cmd == "end":
            secao_texto.append("")
            secao_texto.append("    @ (END) - fim do programa")
            return None

        # WHILE
        if tipo_cmd == "while":
            processarWhileAssembly(no_conteudo)
            return None

        # IF
        if tipo_cmd == "if":
            processarIfAssembly(no_conteudo)
            return None

        # Comando regular: processa usando pilha RPN com informações de tipo da árvore atribuída
        return processarRegularAssembly(no_conteudo)

    def processarWhileAssembly(no_conteudo):
        """Gera Assembly para a estrutura WHILE usando labels de controle de fluxo."""
        label_inicio = obterLabelUnico("while")
        label_fim = f"{label_inicio}_fim"

        filhos = no_conteudo.get("nodos_filhos", [])
        cmd_condicao = None
        sufixo_cmd = None
        for f in filhos:
            if isinstance(f, dict):
                if f.get("nodo_pai") == "comando" and cmd_condicao is None:
                    cmd_condicao = f
                elif f.get("nodo_pai") == "sufixo_comando":
                    sufixo_cmd = f

        cmd_corpo = None
        if sufixo_cmd:
            for f in sufixo_cmd.get("nodos_filhos", []):
                if isinstance(f, dict) and f.get("nodo_pai") == "comando":
                    cmd_corpo = f
                    break

        secao_texto.append("")
        secao_texto.append(f"    @ WHILE - inicio do loop")
        secao_texto.append(f"{label_inicio}:")

        # Avalia a condição (deve retornar um registrador inteiro com 0 ou 1)
        secao_texto.append(f"    @ Avalia condicao do WHILE")
        resultado_cond = None
        if cmd_condicao:
            resultado_cond = processarComandoAssembly(cmd_condicao)

        if resultado_cond:
            reg_cond, tipo_cond = resultado_cond
            # A condição é bool, representada como inteiro: 0 = falso
            secao_texto.append(f"    CMP {reg_cond}, #0")
            secao_texto.append(f"    BEQ {label_fim}             @ se condicao == 0 (falso), sai do loop")

        # Corpo do loop
        secao_texto.append(f"    @ Corpo do WHILE")
        if cmd_corpo:
            processarComandoAssembly(cmd_corpo)

        secao_texto.append(f"    B {label_inicio}               @ volta ao inicio do loop")
        secao_texto.append(f"{label_fim}:")

    def processarIfAssembly(no_conteudo):
        """Gera Assembly para a estrutura IF/ELSE usando labels de controle de fluxo."""
        label_else = obterLabelUnico("if_else")
        label_fim = obterLabelUnico("if_fim")

        filhos = no_conteudo.get("nodos_filhos", [])
        cmd_condicao = None
        sufixo_cmd = None
        for f in filhos:
            if isinstance(f, dict):
                if f.get("nodo_pai") == "comando" and cmd_condicao is None:
                    cmd_condicao = f
                elif f.get("nodo_pai") == "sufixo_comando":
                    sufixo_cmd = f

        cmd_then = None
        apos_cmd = None
        if sufixo_cmd:
            for f in sufixo_cmd.get("nodos_filhos", []):
                if isinstance(f, dict):
                    if f.get("nodo_pai") == "comando":
                        cmd_then = f
                    elif f.get("nodo_pai") == "apos_cmd":
                        apos_cmd = f

        cmd_else = None
        if apos_cmd:
            for f in apos_cmd.get("nodos_filhos", []):
                if isinstance(f, dict) and f.get("nodo_pai") == "comando":
                    cmd_else = f

        secao_texto.append("")
        secao_texto.append(f"    @ IF - Avalia condicao")
        resultado_cond = None
        if cmd_condicao:
            resultado_cond = processarComandoAssembly(cmd_condicao)

        if resultado_cond:
            reg_cond, tipo_cond = resultado_cond
            secao_texto.append(f"    CMP {reg_cond}, #0")
            secao_texto.append(f"    BEQ {label_else}            @ se falso (0), pula pro else")

        # Bloco THEN
        secao_texto.append(f"    @ IF - Bloco THEN (Verdadeiro)")
        if cmd_then:
            processarComandoAssembly(cmd_then)
        secao_texto.append(f"    B {label_fim}               @ fim do then, pula o else")

        # Bloco ELSE
        secao_texto.append(f"{label_else}:")
        secao_texto.append(f"    @ IF - Bloco ELSE (Falso)")
        if cmd_else:
            processarComandoAssembly(cmd_else)

        secao_texto.append(f"{label_fim}:")

    def processarRegularAssembly(no_conteudo):
        """
        Processa um comando regular (expressão RPN) gerando Assembly.
        Usa as anotações de tipo da árvore atribuída para escolher instruções.

        Cada elemento da pilha é uma tupla (registrador, tipo).
        - tipo 'inteiro' ou 'bool': registrador ARM (Rn)
        - tipo 'real': registrador VFP (Dn)

        Retorna (registrador, tipo) do resultado ou None.
        """
        terminais = coletarTerminais(no_conteudo)
        pilha = []  # pilha de tuplas (registrador, tipo)

        # Comentário identificando o comando
        pedacos_expr = []
        for t in terminais:
            tf = t.get("terminal_folha", "")
            if tf not in ("ε", "ABRE_PAREN", "FECHA_PAREN"):
                v = t.get("valor_extraido", "")
                pedacos_expr.append(v if v else tf)
        expr_str = " ".join(pedacos_expr)
        secao_texto.append("")
        secao_texto.append(f"    @ Comando RPN: ( {expr_str} )")

        for terminal in terminais:
            tipo_token = terminal.get("terminal_folha", "")
            valor = terminal.get("valor_extraido", "")
            tipo_anotado = terminal.get("tipo", None)

            # Pula parênteses e epsilon
            if tipo_token in ("ABRE_PAREN", "FECHA_PAREN", "ε"):
                continue

            # NUMERO: carrega constante no registrador adequado ao tipo
            if tipo_token == "NUMERO":
                if tipo_anotado == "inteiro":
                    reg = obterRegInt()
                    nome_const = garantirConstanteInt(valor)
                    secao_texto.append(f"    LDR R4, ={nome_const}")
                    secao_texto.append(f"    LDR {reg}, [R4]              @ carrega inteiro {valor}")
                    pilha.append((reg, "inteiro"))
                else:
                    reg = obterRegFP()
                    nome_const = garantirConstanteDouble(valor)
                    secao_texto.append(f"    LDR R4, ={nome_const}")
                    secao_texto.append(f"    VLDR {reg}, [R4]             @ carrega double {valor}")
                    pilha.append((reg, "real"))

            # OPERADOR aritmético
            elif tipo_token == "OPERADOR":
                if len(pilha) < 2:
                    secao_texto.append(f"    @ ERRO: operandos insuficientes para '{valor}'")
                    continue

                reg_b, tipo_b = pilha.pop()
                reg_a, tipo_a = pilha.pop()
                tipo_resultado = tipo_anotado if tipo_anotado else inferirTipoOperacao(valor, tipo_a, tipo_b)

                # Divisão inteira e resto: sempre operam com inteiros
                if valor in ("/", "%"):
                    # Garantir que operandos estão em registradores inteiros
                    reg_a = converterParaInt(reg_a, tipo_a)
                    reg_b = converterParaInt(reg_b, tipo_b)

                    if valor == "/":
                        # SDIV nao suportado no Cortex-A9: usa VFP para dividir e trunca
                        d_div = obterRegFP()
                        d_dvs = obterRegFP()
                        reg_res = obterRegInt()
                        secao_texto.append(f"    @ divisao inteira via VFP (Cortex-A9 nao suporta SDIV)")
                        secao_texto.append(f"    VMOV S30, {reg_a}")
                        secao_texto.append(f"    VCVT.F64.S32 {d_div}, S30         @ dividendo int -> double")
                        secao_texto.append(f"    VMOV S30, {reg_b}")
                        secao_texto.append(f"    VCVT.F64.S32 {d_dvs}, S30         @ divisor int -> double")
                        secao_texto.append(f"    VDIV.F64 {d_div}, {d_div}, {d_dvs}")
                        secao_texto.append(f"    VCVT.S32.F64 S31, {d_div}         @ trunca para inteiro")
                        secao_texto.append(f"    VMOV {reg_res}, S31")
                        pilha.append((reg_res, "inteiro"))
                    else:  # %
                        # resto: a % b = a - (a/b)*b, divisao via VFP
                        d_div = obterRegFP()
                        d_dvs = obterRegFP()
                        reg_quoc = obterRegInt()
                        reg_res = obterRegInt()
                        secao_texto.append(f"    @ resto via VFP: {reg_a} % {reg_b}")
                        secao_texto.append(f"    VMOV S30, {reg_a}")
                        secao_texto.append(f"    VCVT.F64.S32 {d_div}, S30")
                        secao_texto.append(f"    VMOV S30, {reg_b}")
                        secao_texto.append(f"    VCVT.F64.S32 {d_dvs}, S30")
                        secao_texto.append(f"    VDIV.F64 {d_div}, {d_div}, {d_dvs}  @ quociente real")
                        secao_texto.append(f"    VCVT.S32.F64 S31, {d_div}           @ trunca quociente")
                        secao_texto.append(f"    VMOV {reg_quoc}, S31")
                        secao_texto.append(f"    MUL {reg_res}, {reg_quoc}, {reg_b}")
                        secao_texto.append(f"    SUB {reg_res}, {reg_a}, {reg_res}   @ resto")
                        pilha.append((reg_res, "inteiro"))

                # Divisão real: sempre opera com doubles, resultado real
                elif valor == "|":
                    reg_a = converterParaDouble(reg_a, tipo_a)
                    reg_b = converterParaDouble(reg_b, tipo_b)
                    reg_res = obterRegFP()
                    secao_texto.append(f"    VDIV.F64 {reg_res}, {reg_a}, {reg_b}    @ divisao real")
                    pilha.append((reg_res, "real"))

                # +, -, *, ^: dependem do tipo dos operandos
                elif valor in ("+", "-", "*"):
                    if tipo_resultado == "inteiro":
                        reg_a = converterParaInt(reg_a, tipo_a)
                        reg_b = converterParaInt(reg_b, tipo_b)
                        reg_res = obterRegInt()
                        if valor == "+":
                            secao_texto.append(f"    ADD {reg_res}, {reg_a}, {reg_b}    @ {reg_a} + {reg_b}")
                        elif valor == "-":
                            secao_texto.append(f"    SUB {reg_res}, {reg_a}, {reg_b}    @ {reg_a} - {reg_b}")
                        elif valor == "*":
                            secao_texto.append(f"    MUL {reg_res}, {reg_a}, {reg_b}    @ {reg_a} * {reg_b}")
                        pilha.append((reg_res, "inteiro"))
                    else:
                        reg_a = converterParaDouble(reg_a, tipo_a)
                        reg_b = converterParaDouble(reg_b, tipo_b)
                        reg_res = obterRegFP()
                        if valor == "+":
                            secao_texto.append(f"    VADD.F64 {reg_res}, {reg_a}, {reg_b}    @ soma real")
                        elif valor == "-":
                            secao_texto.append(f"    VSUB.F64 {reg_res}, {reg_a}, {reg_b}    @ subtracao real")
                        elif valor == "*":
                            secao_texto.append(f"    VMUL.F64 {reg_res}, {reg_a}, {reg_b}    @ multiplicacao real")
                        pilha.append((reg_res, "real"))

                elif valor == "^":
                    # Potenciação por loop: base ^ expoente
                    # Converte expoente para inteiro e base para double
                    reg_exp = converterParaInt(reg_b, tipo_b)
                    reg_base = converterParaDouble(reg_a, tipo_a)

                    reg_res = obterRegFP()
                    label_pot = obterLabelUnico("potencia")

                    secao_texto.append(f"    @ potenciacao: base ^ expoente")
                    nome_c1 = garantirConstanteDouble("1.0")
                    secao_texto.append(f"    LDR R4, ={nome_c1}")
                    secao_texto.append(f"    VLDR {reg_res}, [R4]         @ resultado = 1.0")
                    secao_texto.append(f"    MOV R0, {reg_exp}            @ R0 = expoente")
                    secao_texto.append(f"{label_pot}:")
                    secao_texto.append(f"    CMP R0, #0")
                    secao_texto.append(f"    BLE {label_pot}_fim")
                    secao_texto.append(f"    VMUL.F64 {reg_res}, {reg_res}, {reg_base}")
                    secao_texto.append(f"    SUB R0, R0, #1")
                    secao_texto.append(f"    B {label_pot}")
                    secao_texto.append(f"{label_pot}_fim:")

                    if tipo_resultado == "inteiro":
                        # Trunca de volta para inteiro
                        reg_int_res = obterRegInt()
                        secao_texto.append(f"    VCVT.S32.F64 S31, {reg_res}")
                        secao_texto.append(f"    VMOV {reg_int_res}, S31      @ resultado inteiro")
                        pilha.append((reg_int_res, "inteiro"))
                    else:
                        pilha.append((reg_res, "real"))

            # OPERADOR RELACIONAL: resultado sempre bool (inteiro 0 ou 1)
            elif tipo_token == "OPERADOR_REL":
                if len(pilha) < 2:
                    secao_texto.append(f"    @ ERRO: operandos insuficientes para '{valor}'")
                    continue

                reg_b, tipo_b = pilha.pop()
                reg_a, tipo_a = pilha.pop()
                reg_res = obterRegInt()

                label_verdade = obterLabelUnico("rel_verdade")
                label_rel_fim = obterLabelUnico("rel_fim")

                secao_texto.append(f"    @ comparacao relacional '{valor}'")

                # Se ambos são inteiros ou bool, compara com CMP
                if tipo_a in ("inteiro", "bool") and tipo_b in ("inteiro", "bool"):
                    secao_texto.append(f"    CMP {reg_a}, {reg_b}")
                else:
                    # Ao menos um é real: promove ambos para double e compara com VFP
                    reg_a = converterParaDouble(reg_a, tipo_a)
                    reg_b = converterParaDouble(reg_b, tipo_b)
                    secao_texto.append(f"    VCMP.F64 {reg_a}, {reg_b}")
                    secao_texto.append(f"    VMRS APSR_nzcv, FPSCR")

                # Branch condicional
                if valor == "<":
                    secao_texto.append(f"    BLT {label_verdade}")
                elif valor == ">":
                    secao_texto.append(f"    BGT {label_verdade}")
                elif valor == "==":
                    secao_texto.append(f"    BEQ {label_verdade}")
                elif valor == "!=":
                    secao_texto.append(f"    BNE {label_verdade}")
                elif valor == "<=":
                    secao_texto.append(f"    BLE {label_verdade}")
                elif valor == ">=":
                    secao_texto.append(f"    BGE {label_verdade}")

                # Falso: resultado = 0
                secao_texto.append(f"    MOV {reg_res}, #0            @ false")
                secao_texto.append(f"    B {label_rel_fim}")

                # Verdadeiro: resultado = 1
                secao_texto.append(f"{label_verdade}:")
                secao_texto.append(f"    MOV {reg_res}, #1            @ true")

                secao_texto.append(f"{label_rel_fim}:")
                pilha.append((reg_res, "bool"))

            # MEMORIA: load ou store
            elif tipo_token == "MEMORIA":
                cat_semantica = terminal.get("categoria_semantica", "")

                if cat_semantica == "var_store" and len(pilha) > 0:
                    # STORE: consome o valor do topo da pilha e armazena na memória
                    reg_valor, tipo_valor = pilha.pop()
                    nome_label = garantirMemoria(valor, tipo_valor)

                    if tipo_valor == "real":
                        reg_valor = converterParaDouble(reg_valor, tipo_valor)
                        secao_texto.append(f"    LDR R0, ={nome_label}        @ store em {valor}")
                        secao_texto.append(f"    VSTR {reg_valor}, [R0]")
                    else:
                        reg_valor = converterParaInt(reg_valor, tipo_valor)
                        secao_texto.append(f"    LDR R0, ={nome_label}        @ store em {valor}")
                        secao_texto.append(f"    STR {reg_valor}, [R0]")

                else:
                    # LOAD: carrega valor da memória
                    tipo_mem = tipo_anotado if tipo_anotado else "real"
                    nome_label = garantirMemoria(valor, tipo_mem)

                    if tipo_mem == "real":
                        reg_carregado = obterRegFP()
                        secao_texto.append(f"    LDR R0, ={nome_label}        @ load de {valor}")
                        secao_texto.append(f"    VLDR {reg_carregado}, [R0]")
                        pilha.append((reg_carregado, "real"))
                    else:
                        reg_carregado = obterRegInt()
                        secao_texto.append(f"    LDR R0, ={nome_label}        @ load de {valor}")
                        secao_texto.append(f"    LDR {reg_carregado}, [R0]")
                        pilha.append((reg_carregado, tipo_mem))

            # KEYWORD_RES: acessa histórico de resultados
            elif tipo_token == "KEYWORD_RES":
                if len(pilha) < 1:
                    secao_texto.append(f"    @ ERRO: falta N para RES")
                    continue

                reg_n, tipo_n = pilha.pop()
                reg_n = converterParaInt(reg_n, tipo_n)
                reg_res = obterRegFP()

                secao_texto.append(f"    @ RES: acessa resultado anterior")
                secao_texto.append(f"    LDR R1, =resultados")
                secao_texto.append(f"    LDR R2, =numResultados")
                secao_texto.append(f"    LDR R2, [R2]                @ R2 = contador total")
                secao_texto.append(f"    SUB R2, R2, {reg_n}         @ indice = total - N")
                secao_texto.append(f"    LSL R2, R2, #3              @ offset em bytes (double = 8)")
                secao_texto.append(f"    ADD R1, R1, R2")
                secao_texto.append(f"    VLDR {reg_res}, [R1]        @ carrega resultado historico")

                tipo_resultado_res = tipo_anotado if tipo_anotado else "real"
                pilha.append((reg_res, tipo_resultado_res))

        # Armazena resultado no histórico (se a pilha tiver exatamente 1 valor)
        if len(pilha) == 1:
            reg_final, tipo_final = pilha[0]

            # Converte resultado para double antes de armazenar no histórico
            reg_double = converterParaDouble(reg_final, tipo_final)

            secao_texto.append(f"    @ Armazena resultado no historico")
            secao_texto.append(f"    LDR R0, =numResultados")
            secao_texto.append(f"    LDR R1, [R0]                @ R1 = numResultados atual")
            secao_texto.append(f"    LDR R2, =resultados")
            secao_texto.append(f"    LSL R3, R1, #3              @ offset = R1 * 8")
            secao_texto.append(f"    ADD R2, R2, R3")
            secao_texto.append(f"    VSTR {reg_double}, [R2]     @ guarda resultado")
            secao_texto.append(f"    ADD R1, R1, #1")
            secao_texto.append(f"    STR R1, [R0]                @ numResultados++")

            return pilha[0]

        return None

    def converterParaDouble(reg, tipo_atual):
        """Converte um registrador inteiro/bool para double VFP, se necessário."""
        if tipo_atual == "real":
            return reg  # já é VFP double
        # tipo_atual é 'inteiro' ou 'bool' → converter de ARM int para VFP double
        reg_fp = obterRegFP()
        secao_texto.append(f"    VMOV S30, {reg}              @ copia int para VFP")
        secao_texto.append(f"    VCVT.F64.S32 {reg_fp}, S30   @ converte int para double")
        return reg_fp

    def converterParaInt(reg, tipo_atual):
        """Converte um registrador VFP double para inteiro ARM, se necessário."""
        if tipo_atual in ("inteiro", "bool"):
            return reg  # já é inteiro ARM
        # tipo_atual é 'real' → trunca de double para int
        reg_int = obterRegInt()
        secao_texto.append(f"    VCVT.S32.F64 S31, {reg}     @ trunca double para int")
        secao_texto.append(f"    VMOV {reg_int}, S31           @ copia para ARM")
        return reg_int

    def percorrerArvoreAssembly(no):
        """Percorre a árvore atribuída buscando nós 'comando'."""
        if not isinstance(no, dict):
            return

        nome_no = no.get("nodo_pai", "")

        if nome_no == "comando":
            processarComandoAssembly(no)
            return
        elif nome_no == "comando_descartado":
            secao_texto.append("")
            secao_texto.append(f"    @ AVISO: linha ignorada. Motivo: {no.get('motivo', 'Desconhecido')}")
            return

        if "nodos_filhos" in no:
            for filho in no["nodos_filhos"]:
                percorrerArvoreAssembly(filho)

    # ========== Execução principal da geração de Assembly ==========

    # Percorre a árvore atribuída
    percorrerArvoreAssembly(arvore_atribuida)

    # Adiciona histórico de resultados ao .data
    secao_dados.append("    .align 3")
    secao_dados.append("    resultados: .space 800       @ espaco para 100 doubles")
    secao_dados.append("    numResultados: .word 0")

    # Monta o código final
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
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            for linha in codigo_final:
                f.write(linha + "\n")
        print(f"Assembly gerado e salvo em '{nome_arquivo}'.")
    except Exception as e:
        print(f"Erro ao salvar Assembly: {e}")

    return codigo_final

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

    if possuiErroLexico(tokens):
        print("Análise semântica não executada devido a erros anteriores.")
        return

    if possuiErroSintatico(arvore_sintatica_inicial):
        print("\nResultado da análise sintática: FALHOU")
        print("Análise semântica não executada (erros sintáticos encontrados).")
        return

    print("\nResultado da análise sintática: OK\n")

    print(f"{'='*60}")
    print("ANÁLISE SEMÂNTICA")
    print(f"{'='*60}\n")

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
        # Aluno 4: Gera a árvore atribuída se não houver erros
        arvore_atribuida = gerarArvoreAtribuida(arvore_sintatica_inicial, tabela_simbolos)

        # Gera código Assembly ARMv7 a partir da árvore atribuída
        nome_assembly = nome_arquivo.replace(".txt", ".s")
        gerarAssembly(arvore_atribuida, nome_assembly)

    print(f"\n{'='*60}")
    print("ARQUIVOS DE SAÍDA GERADOS")
    print(f"{'='*60}")
    print("  - tabela_simbolos.md")
    print("  - erros_semanticos.md")
    print("  - relatorio_tipos.md")
    print("  - arvore_sintatica.md")
    print("  - arvore_sintatica.json")
    if not todos_erros:
        print("  - arvore_atribuida.json")
        print("  - arvore_atribuida.md")
        nome_assembly = nome_arquivo.replace(".txt", ".s")
        print(f"  - {nome_assembly}")
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
