# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7
from sintatico import construirGramatica, parsear
from lexico import parseExpressao


def testarConstruirGramatica():
    """
    Valida que a gramática foi construída com a quantidade correta de não-terminais e produções.
    """
    print("=" * 50)
    print("Teste: construirGramatica()\n")

    resultado_gramatica = construirGramatica()
    regras_producao = resultado_gramatica["gramatica"]

    aprovados = 0
    reprovados = 0

    # Verifica quantidade de não-terminais (deve ser 10)
    quantidade_nao_terminais = len(regras_producao)
    nao_terminais_esperados = [
        "programa", "comando_lista", "comando", "conteudo_comando",
        "sufixo_numero", "sufixo_memoria", "sufixo_comando",
        "operador_final", "apos_mem", "apos_cmd"
    ]

    passou = quantidade_nao_terminais == len(nao_terminais_esperados)
    status = "OK" if passou else "FALHOU"
    print(f"{status} | Quantidade de não-terminais: {quantidade_nao_terminais} (esperado: {len(nao_terminais_esperados)})")
    if passou:
        aprovados += 1
    else:
        reprovados += 1

    # Verifica que todos os não-terminais esperados existem
    for nome_nt in nao_terminais_esperados:
        existe = nome_nt in regras_producao
        status = "OK" if existe else "FALHOU"
        print(f"{status} | Não-terminal '{nome_nt}' existe na gramática")
        if existe:
            aprovados += 1
        else:
            reprovados += 1

    # Verifica que a gramática é LL(1) válida
    eh_valida = resultado_gramatica["eh_valida"]
    status = "OK" if eh_valida else "FALHOU"
    print(f"{status} | Gramática é LL(1) válida (sem conflitos)")
    if eh_valida:
        aprovados += 1
    else:
        reprovados += 1

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarCalcularFirst():
    """
    Valida os conjuntos FIRST contra os valores esperados.
    """
    print("=" * 50)
    print("Teste: calcularFirst()\n")

    resultado_gramatica = construirGramatica()
    conjuntos_first = resultado_gramatica["first"]

    aprovados = 0
    reprovados = 0

    # Valores esperados para cada FIRST
    valores_esperados = {
        "programa": {"ABRE_PAREN", "ε"},
        "comando_lista": {"ABRE_PAREN", "ε"},
        "comando": {"ABRE_PAREN"},
        "conteudo_comando": {"KEYWORD_START", "KEYWORD_END", "NUMERO", "MEMORIA", "ABRE_PAREN"},
        "sufixo_numero": {"KEYWORD_RES", "NUMERO", "MEMORIA", "ABRE_PAREN"},
        "sufixo_memoria": {"NUMERO", "MEMORIA", "ABRE_PAREN", "ε"},
        "sufixo_comando": {"NUMERO", "MEMORIA", "ABRE_PAREN", "ε"},
        "operador_final": {"OPERADOR", "OPERADOR_REL"},
        "apos_mem": {"OPERADOR", "OPERADOR_REL", "ε"},
        "apos_cmd": {"OPERADOR", "OPERADOR_REL", "KEYWORD_WHILE", "ABRE_PAREN"},
    }

    for nao_terminal, first_esperado in valores_esperados.items():
        first_calculado = conjuntos_first.get(nao_terminal, set())
        passou = first_calculado == first_esperado

        status = "OK" if passou else "FALHOU"
        print(f"{status} | FIRST({nao_terminal})")

        if not passou:
            print(f"        Esperado: {sorted(first_esperado)}")
            print(f"        Obtido:   {sorted(first_calculado)}")

        if passou:
            aprovados += 1
        else:
            reprovados += 1

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarCalcularFollow():
    """
    Valida os conjuntos FOLLOW contra os valores esperados.
    """
    print("=" * 50)
    print("Teste: calcularFollow()\n")

    resultado_gramatica = construirGramatica()
    conjuntos_follow = resultado_gramatica["follow"]

    aprovados = 0
    reprovados = 0

    # Valores esperados para cada FOLLOW
    valores_esperados = {
        "programa": {"$"},
        "comando_lista": {"$"},
        "conteudo_comando": {"FECHA_PAREN"},
        "sufixo_numero": {"FECHA_PAREN"},
        "sufixo_memoria": {"FECHA_PAREN"},
        "sufixo_comando": {"FECHA_PAREN"},
        "operador_final": {"FECHA_PAREN"},
        "apos_mem": {"FECHA_PAREN"},
        "apos_cmd": {"FECHA_PAREN"},
    }

    for nao_terminal, follow_esperado in valores_esperados.items():
        follow_calculado = conjuntos_follow.get(nao_terminal, set())
        passou = follow_calculado == follow_esperado

        status = "OK" if passou else "FALHOU"
        print(f"{status} | FOLLOW({nao_terminal})")

        if not passou:
            print(f"        Esperado: {sorted(follow_esperado)}")
            print(f"        Obtido:   {sorted(follow_calculado)}")

        if passou:
            aprovados += 1
        else:
            reprovados += 1

    # FOLLOW(comando) tem muitos elementos, verifica se contém os essenciais
    follow_comando = conjuntos_follow.get("comando", set())
    elementos_essenciais_comando = {"ABRE_PAREN", "$", "FECHA_PAREN", "OPERADOR", "OPERADOR_REL"}
    contem_essenciais = elementos_essenciais_comando.issubset(follow_comando)

    status = "OK" if contem_essenciais else "FALHOU"
    print(f"{status} | FOLLOW(comando) contém elementos essenciais")
    if not contem_essenciais:
        print(f"        Obrigatórios: {sorted(elementos_essenciais_comando)}")
        print(f"        Obtido:       {sorted(follow_comando)}")

    if contem_essenciais:
        aprovados += 1
    else:
        reprovados += 1

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarTabelaLL1():
    """
    Valida que a tabela LL(1) não tem conflitos e contém entradas esperadas.
    """
    print("=" * 50)
    print("Teste: construirTabelaLL1()\n")

    resultado_gramatica = construirGramatica()
    tabela_ll1 = resultado_gramatica["tabela_ll1"]

    aprovados = 0
    reprovados = 0

    # Verifica ausência de conflitos
    eh_valida = resultado_gramatica["eh_valida"]
    status = "OK" if eh_valida else "FALHOU"
    print(f"{status} | Tabela sem conflitos")
    if eh_valida:
        aprovados += 1
    else:
        reprovados += 1

    # Verifica entradas chave da tabela
    entradas_esperadas = [
        # Programa e lista de comandos
        ("programa", "ABRE_PAREN"),
        ("programa", "$"),
        ("comando_lista", "ABRE_PAREN"),
        ("comando_lista", "$"),
        # Comando
        ("comando", "ABRE_PAREN"),
        # Conteúdo do comando
        ("conteudo_comando", "KEYWORD_START"),
        ("conteudo_comando", "KEYWORD_END"),
        ("conteudo_comando", "NUMERO"),
        ("conteudo_comando", "MEMORIA"),
        ("conteudo_comando", "ABRE_PAREN"),
        # Sufixos
        ("sufixo_numero", "KEYWORD_RES"),
        ("sufixo_numero", "NUMERO"),
        ("sufixo_numero", "MEMORIA"),
        ("sufixo_memoria", "FECHA_PAREN"),
        # Controle
        ("apos_cmd", "KEYWORD_WHILE"),
        ("apos_cmd", "ABRE_PAREN"),
    ]

    for chave_esperada in entradas_esperadas:
        existe = chave_esperada in tabela_ll1
        nao_terminal, terminal = chave_esperada

        status = "OK" if existe else "FALHOU"
        print(f"{status} | M[{nao_terminal}, {terminal}] existe na tabela")

        if existe:
            aprovados += 1
        else:
            reprovados += 1

    # Verifica produções específicas
    producao_start = tabela_ll1.get(("conteudo_comando", "KEYWORD_START"), [])
    passou_start = producao_start == ["KEYWORD_START"]
    status = "OK" if passou_start else "FALHOU"
    print(f"{status} | M[conteudo_comando, KEYWORD_START] = KEYWORD_START")
    if passou_start:
        aprovados += 1
    else:
        reprovados += 1

    producao_res = tabela_ll1.get(("sufixo_numero", "KEYWORD_RES"), [])
    passou_res = producao_res == ["KEYWORD_RES"]
    status = "OK" if passou_res else "FALHOU"
    print(f"{status} | M[sufixo_numero, KEYWORD_RES] = KEYWORD_RES")
    if passou_res:
        aprovados += 1
    else:
        reprovados += 1

    producao_while = tabela_ll1.get(("apos_cmd", "KEYWORD_WHILE"), [])
    passou_while = producao_while == ["KEYWORD_WHILE"]
    status = "OK" if passou_while else "FALHOU"
    print(f"{status} | M[apos_cmd, KEYWORD_WHILE] = KEYWORD_WHILE")
    if passou_while:
        aprovados += 1
    else:
        reprovados += 1

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarParsear():
    """
    Valida a execução do parser com tokens simulados de expressões.
    Casos de teste: (3.14 2.0 +), ((A B +) (C D *) /), (A B + C)
    """
    print("\nTeste: parsear() com Recuperação de Erros (Panic Mode)\n")
    
    # Constrói a gramática e obtém a tabela LL(1)
    resultado_gramatica = construirGramatica()
    tabela_ll1 = resultado_gramatica["tabela_ll1"]
    
    # Lista de casos de teste com a indicação se deve gerar erro ou não
    testes = [
        {"expressao": "( 3.14 2.0 + )", "espera_erro": False},
        {"expressao": "( ( A B + ) ( C D * ) / )", "espera_erro": False},
        {"expressao": "( A B + C )", "espera_erro": True}
    ]
    
    aprovados = 0
    reprovados = 0
    
    # Verifica recursivamente se a AST contém nodos com erro
    def ast_tem_erros(nodo):
        if "erro" in nodo or "erro_nodo_pai" in nodo or "erro_sintatico" in nodo:
            return True
        for filho in nodo.get("nodos_filhos", []):
            if ast_tem_erros(filho):
                return True
        return False
    
    for teste in testes:
        texto = teste["expressao"]
        vetor_tokens = []
        
        # Gera os tokens da expressão usando o analisador léxico
        parseExpressao(texto, vetor_tokens)
        
        # Coloca dentro de uma lista pois o parsear espera lista de linhas
        fita_preparada = [vetor_tokens]
        
        print(f" Testando expressão: {texto}")
        print(" Log das validações LL(1) durante o parsing:")
        
        # Executa o parser — captura LinhaDescartada quando o erro é irrecuperável
        try:
            ast_gerada = parsear(fita_preparada, tabela_ll1)
        except Exception:
            ast_gerada = None

        teve_erro_real = True if ast_gerada is None else ast_tem_erros(ast_gerada)
        status_sucesso = (teve_erro_real == teste["espera_erro"])
        
        status_text = "OK" if status_sucesso else "FALHOU"
        detalhe_erro = " (Panic Mode detectou o erro corretamente!)" if (teste["espera_erro"] and status_sucesso) else ""
        
        print(f" -> Resultado do Teste no Parser: {status_text}{detalhe_erro}\n")
        
        if status_sucesso:
            aprovados += 1
        else:
            reprovados += 1

    print(f"Resultado: {aprovados} aprovados, {reprovados} reprovados\n")

def iniciarTestesSintatico():
    """
    Executa todos os testes do analisador sintático.
    """
    print("\nRealização dos testes do analisador sintático:\n")
    testarConstruirGramatica()
    testarCalcularFirst()
    testarCalcularFollow()
    testarTabelaLL1()
    testarParsear()


# Execução direta para testes
if __name__ == "__main__":
    iniciarTestesSintatico()
