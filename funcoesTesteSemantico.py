# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

import os
import io
import contextlib

from lexico import parseExpressao
from sintatico import construirGramatica, gerarTokens, lerTokens, parsear, gerarArvore
from semantico import (
    prepararEntradaSemantica,
    construirTabelaSimbolos,
    verificarTipos,
    decorarArvoreComLinhas,
    possuiErroLexico,
    possuiErroSintatico,
    gerarArvoreAtribuida,
)

# Nome do arquivo temporário usado pelos testes para simular entradas
ARQUIVO_TEMP = "aux_teste_semantico.txt"


def auxAnalisarPrograma(linhas_codigo):
    """
    Auxiliar: recebe lista de linhas de código, escreve arquivo temporário e
    executa o pipeline completo (lexico -> sintatico -> semantico).
    Suprime a saída padrão durante a análise para manter o output dos testes limpo.
    Retorna (tabela_simbolos, erros_declaracao, erros_tipo).
    Retorna (None, [], []) se houver erro léxico ou sintático.
    """
    # Escreve o código de teste no arquivo temporário
    with open(ARQUIVO_TEMP, "w", encoding="utf-8") as arquivo_temp:
        for linha in linhas_codigo:
            arquivo_temp.write(linha + "\n")

    try:
        # Redireciona stdout para suprimir logs do pipeline durante os testes
        saida_descartada = io.StringIO()
        with contextlib.redirect_stdout(saida_descartada):
            tokens, arvore = prepararEntradaSemantica(ARQUIVO_TEMP)

            # Interrompe se houver erro léxico ou sintático antes da semântica
            if possuiErroLexico(tokens) or possuiErroSintatico(arvore):
                return None, [], []

            # Executa o pipeline semântico completo
            decorarArvoreComLinhas(arvore, tokens)
            tabela, erros_decl = construirTabelaSimbolos(arvore)
            erros_tipo = verificarTipos(arvore, tabela)

        return tabela, erros_decl, erros_tipo

    finally:
        # Remove o arquivo temporário independente do resultado
        if os.path.exists(ARQUIVO_TEMP):
            os.remove(ARQUIVO_TEMP)


def auxContemMensagem(erros, trecho):
    """Retorna True se algum erro contém o trecho (case-insensitive)."""
    # Percorre todos os erros procurando o trecho informado
    for erro in erros:
        if trecho.lower() in erro.get("mensagem", "").lower():
            return True
    return False


def testarLiteraisETiposBasicos():
    """
    Valida que operações entre tipos compatíveis não geram erros de tipo.
    Cobre: int+int, real+int, int*real, / e % com inteiros, | e ^.
    """
    print("=" * 50)
    print("Teste: literais e tipos basicos\n")

    # Todos os casos abaixo devem ser aceitos sem nenhum erro de tipo
    casos = [
        ("inteiro + inteiro -> sem erro",  ["(START)", "(3 2 +)",      "(END)"], True),
        ("real + inteiro -> sem erro",     ["(START)", "(3.5 2 +)",    "(END)"], True),
        ("inteiro * real -> sem erro",     ["(START)", "(4 2.0 *)",    "(END)"], True),
        ("inteiro / inteiro -> sem erro",  ["(START)", "(10 3 /)",     "(END)"], True),
        ("inteiro % inteiro -> sem erro",  ["(START)", "(10 3 %)",     "(END)"], True),
        ("real | real -> sem erro",        ["(START)", "(10.0 3.0 |)", "(END)"], True),
        ("inteiro ^ inteiro -> sem erro",  ["(START)", "(2 8 ^)",      "(END)"], True),
        ("real - real -> sem erro",        ["(START)", "(5.0 2.0 -)",  "(END)"], True),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline semântico para o caso atual
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarDivisaoInteiraEResto():
    """
    Valida que os operadores '/' e '%' rejeitam operandos 'real'.
    Casos invalidos: real/inteiro, inteiro/real, real/real.
    Casos validos: inteiro/inteiro, inteiro%inteiro.
    """
    print("=" * 50)
    print("Teste: divisao inteira (/) e resto (%)\n")

    # Primeiros dois casos são validos; os demais devem gerar erro de tipo
    casos = [
        ("inteiro / inteiro -> sem erro",  ["(START)", "(10 3 /)",    "(END)"], True),
        ("inteiro % inteiro -> sem erro",  ["(START)", "(10 3 %)",    "(END)"], True),
        ("real / inteiro -> ERRO",         ["(START)", "(3.5 2 /)",   "(END)"], False),
        ("inteiro / real -> ERRO",         ["(START)", "(10 3.0 /)",  "(END)"], False),
        ("real / real -> ERRO",            ["(START)", "(3.5 2.0 /)", "(END)"], False),
        ("real % inteiro -> ERRO",         ["(START)", "(3.5 2 %)",   "(END)"], False),
        ("inteiro % real -> ERRO",         ["(START)", "(10 3.0 %)",  "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline e verifica se houve erro de tipo
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarBoolEmAritmetica():
    """
    Valida que 'bool' é rejeitado como operando de operadores aritmeticos.
    Bool é produzido por operadores relacionais (ex: 3 2 <).
    """
    print("=" * 50)
    print("Teste: bool em operadores aritmeticos\n")

    # Todos os casos abaixo devem gerar erro: bool nao pode ser usado em aritmetica
    casos = [
        ("bool + inteiro -> ERRO",  ["(START)", "((3 2 <) 5 +)",    "(END)"], False),
        ("bool - inteiro -> ERRO",  ["(START)", "((3 2 <) 5 -)",    "(END)"], False),
        ("bool * inteiro -> ERRO",  ["(START)", "((3 2 <) 5 *)",    "(END)"], False),
        ("bool | real -> ERRO",     ["(START)", "((3 2 <) 5.0 |)",  "(END)"], False),
        ("bool / inteiro -> ERRO",  ["(START)", "((3 2 <) 2 /)",    "(END)"], False),
        ("bool % inteiro -> ERRO",  ["(START)", "((3 2 <) 2 %)",    "(END)"], False),
        ("inteiro + bool -> ERRO",  ["(START)", "(5 (3 2 <) +)",    "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline e verifica se o erro de bool foi detectado
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarOperadoresRelacionais():
    """
    Valida as regras dos operadores relacionais:
    - <, >, <=, >= aceitam apenas numericos e produzem bool
    - ==, != aceitam dois bools ou dois numericos; rejeitam tipos mistos
    """
    print("=" * 50)
    print("Teste: operadores relacionais\n")

    casos = [
        # Casos validos: operandos numericos ou bools compativeis
        ("int < int -> bool, sem erro",          ["(START)", "(3 2 <)",                   "(END)"], True),
        ("real > real -> bool, sem erro",         ["(START)", "(3.0 2.0 >)",               "(END)"], True),
        ("int <= real -> bool, sem erro",         ["(START)", "(3 2.0 <=)",                "(END)"], True),
        ("int == int -> bool, sem erro",          ["(START)", "(3 3 ==)",                  "(END)"], True),
        ("bool == bool -> bool, sem erro",        ["(START)", "((3 2 <) (1 0 >) ==)",      "(END)"], True),
        ("real != real -> bool, sem erro",        ["(START)", "(3.0 2.0 !=)",              "(END)"], True),
        # Casos invalidos: uso de bool com operadores de ordenacao ou tipos mistos
        ("bool < inteiro -> ERRO",                ["(START)", "((3 2 <) 5 <)",             "(END)"], False),
        ("bool > inteiro -> ERRO",                ["(START)", "((3 2 <) 5 >)",             "(END)"], False),
        ("bool != inteiro -> ERRO incompativel",  ["(START)", "((3 2 <) 5 !=)",            "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline e avalia o resultado esperado
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarCondicoesControle():
    """
    Valida que as condicoes de IF e WHILE devem produzir 'bool'.
    Condicoes com tipo inteiro ou real devem gerar erro semantico.
    """
    print("=" * 50)
    print("Teste: condicoes de IF e WHILE\n")

    casos = [
        # Casos validos: condicao produz bool via operador relacional
        ("WHILE cond bool -> sem erro",    ["(START)", "((3 2 <) (5 3 *) WHILE)",           "(END)"], True),
        ("IF cond bool -> sem erro",       ["(START)", "((3 2 ==) (1 2 +) (3 4 +) IF)",     "(END)"], True),
        # Casos invalidos: condicao produz inteiro ou real
        ("WHILE cond inteiro -> ERRO",     ["(START)", "((1 2 +) (3 4 *) WHILE)",           "(END)"], False),
        ("WHILE cond real -> ERRO",        ["(START)", "((3.0 2.0 +) (3 4 *) WHILE)",       "(END)"], False),
        ("IF cond inteiro -> ERRO",        ["(START)", "((1 2 +) (1 3 +) (2 4 +) IF)",      "(END)"], False),
        ("IF cond real -> ERRO",           ["(START)", "((3.0 2.0 +) (1 2 +) (3 4 +) IF)", "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline e verifica se a condicao foi validada corretamente
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarExpressoesAninhadas():
    """
    Valida expressões aninhadas com tipos compatíveis (sem erro)
    e expressões aninhadas com incompatibilidades de tipos (com erro).
    """
    print("=" * 50)
    print("Teste: expressoes aninhadas\n")

    casos = [
        # Casos validos: tipos numericos combinados em varios niveis de aninhamento
        ("(A+B) | (C*D) -> real, sem erro",   ["(START)", "((3 2 +) (4 5 *) |)",      "(END)"], True),
        ("(A%B) / (C*D) -> int, sem erro",    ["(START)", "((10 3 %) (4 2 *) /)",     "(END)"], True),
        ("((A+B)*C)-D -> real, sem erro",     ["(START)", "(((2 3 +) 4 *) 5.0 -)",    "(END)"], True),
        # Casos invalidos: bool produzido em nivel interno e usado em operacao invalida
        ("bool aninhado em / -> ERRO",        ["(START)", "((3 2 <) 2 /)",             "(END)"], False),
        ("bool aninhado em % -> ERRO",        ["(START)", "(5 (3 2 <) %)",             "(END)"], False),
        ("bool aninhado em + -> ERRO",        ["(START)", "((3 2 <) (1 2 +) +)",      "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline e verifica se o aninhamento foi tratado corretamente
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarVariaveisMemoria():
    """
    Valida que variáveis são corretamente inferidas e reutilizadas,
    e que redefinições incompatíveis de tipo geram erro.
    """
    print("=" * 50)
    print("Teste: variaveis e memoria\n")

    casos = [
        # Casos validos: store seguido de load com o mesmo tipo
        ("store/load de real -> sem erro",       ["(START)", "(5.0 VAR)", "(VAR)",   "(END)"], True),
        ("store/load de inteiro -> sem erro",    ["(START)", "(5 CONT)", "(CONT)",   "(END)"], True),
        # Casos invalidos: uso antes de definir e redefinicao com tipo diferente
        ("var usada antes de definir -> ERRO",   ["(START)", "(VAR)",               "(END)"], False),
        ("redef incompativel (int->real) -> ERRO",["(START)", "(5 X)", "(3.0 X)",   "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        # Executa o pipeline e verifica se a variavel foi tratada corretamente
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            # Exibe os erros inesperados para facilitar o diagnóstico
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarArvoreAtribuida():
    """
    Valida a geracao da arvore atribuida (aumentada), verificando se os arquivos
    'arvore_atribuida.json' e 'arvore_atribuida.md' sao criados e contem as decoracoes.
    """
    print("=" * 50)
    print("Teste: geracao da arvore atribuida (Aluno 4)\n")

    # Programa simples para teste
    codigo = [
        "(START)",
        "(5.0 VAR)",
        "(VAR)",
        "(END)"
    ]

    # Remove os arquivos se ja existirem para garantir que foram recriados
    for nome_arq in ("arvore_atribuida.json", "arvore_atribuida.md"):
        if os.path.exists(nome_arq):
            os.remove(nome_arq)

    # Executa a analise
    tabela, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)

    passou = False
    if tabela is not None and len(erros_decl) == 0 and len(erros_tipo) == 0:
        try:
            # Escreve o codigo no arquivo temporario
            with open(ARQUIVO_TEMP, "w", encoding="utf-8") as arquivo_temp:
                for linha in codigo:
                    arquivo_temp.write(linha + "\n")

            tokens, arvore = prepararEntradaSemantica(ARQUIVO_TEMP)
            decorarArvoreComLinhas(arvore, tokens)
            tabela, _ = construirTabelaSimbolos(arvore)

            # Gera a arvore atribuida
            arvore_atrib = gerarArvoreAtribuida(arvore, tabela)

            # Verifica se os arquivos foram criados e tem o conteudo esperado
            tem_json = os.path.exists("arvore_atribuida.json")
            tem_md = os.path.exists("arvore_atribuida.md")

            # Verifica se a decoracao esta correta lendo o MD
            conteudo_md = ""
            if tem_md:
                with open("arvore_atribuida.md", "r", encoding="utf-8") as arquivo_atrib_md:
                    conteudo_md = arquivo_atrib_md.read()

            contem_tipo_cat = "tipo: real, cat: var_store" in conteudo_md and "tipo: real, cat: var_load" in conteudo_md

            if tem_json and tem_md and contem_tipo_cat:
                passou = True
        except Exception as e:
            print(f"       Erro na execucao do teste: {e}")
        finally:
            if os.path.exists(ARQUIVO_TEMP):
                os.remove(ARQUIVO_TEMP)

    if passou:
        status = "OK"
        print(f"{status} | arvore atribuida gerada com sucesso e devidamente decorada")
    else:
        status = "FALHOU"
        print(f"{status} | falha na geracao ou decoracao da arvore atribuida")

    print(f"\nResultado: {1 if passou else 0} aprovados, {0 if passou else 1} reprovados")
    print("=" * 50 + "\n")


def testarErrosLexicos():
    """
    Valida que o pipeline semântico aborta ao encontrar tokens léxicos inválidos.
    O analisador não deve prosseguir para a etapa semântica quando há erros léxicos.
    """
    print("=" * 50)
    print("Teste: erros lexicos\n")

    # Em todos os casos abaixo espera-se que o pipeline aborte (tabela retorna None)
    casos = [
        ("token invalido '@' -> aborta semantico",
         ["(START)", "(3 @ 2 +)", "(END)"], True),
        ("numero mal-formado '3.1.4' -> aborta semantico",
         ["(START)", "(3.1.4 2 +)", "(END)"], True),
        ("identificador minusculo 'var' -> aborta semantico",
         ["(START)", "(5 var)", "(END)"], True),
        ("programa valido -> nao aborta",
         ["(START)", "(3 2 +)", "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_abortar in casos:
        tabela, _, _ = auxAnalisarPrograma(codigo)
        abortou = (tabela is None)
        passou = (espera_abortar == abortou)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarErrosSintaticos():
    """
    Valida que o pipeline semântico aborta ao encontrar erros sintáticos.
    Cobre ausência de START/END e expressões com estrutura inválida.
    """
    print("=" * 50)
    print("Teste: erros sintaticos\n")

    casos = [
        # Ausência de marcadores obrigatórios
        ("sem (START) -> aborta semantico",
         ["(3 2 +)", "(END)"], True),
        ("sem (END) -> aborta semantico",
         ["(START)", "(3 2 +)"], True),
        # Expressão com estrutura inválida: dois números sem operador
        ("expressao '(3 2)' sem operador -> aborta semantico",
         ["(START)", "(3 2)", "(END)"], True),
        # Programa mínimo válido (só START e END)
        ("programa minimo valido -> nao aborta",
         ["(START)", "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_abortar in casos:
        tabela, _, _ = auxAnalisarPrograma(codigo)
        abortou = (tabela is None)
        passou = (espera_abortar == abortou)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarComentarios():
    """
    Valida que comentários *{...}* são ignorados pelo léxico e não interferem
    na análise semântica. Cobre: comentário em linha inteira, no final de linha
    e no meio de expressão. Também valida que comentário não fechado aborta o pipeline.
    """
    print("=" * 50)
    print("Teste: comentarios em diferentes posicoes\n")

    casos = [
        # Comentários em posições diferentes não devem gerar erros semânticos
        ("comentario em linha inteira -> sem erro",
         ["(START)", "*{ comentario em linha inteira }*", "(5.0 VAR)", "(VAR)", "(END)"],
         False),
        ("comentario no final de linha -> sem erro",
         ["(START)", "(5.0 VAR) *{ comentario no final }*", "(VAR)", "(END)"],
         False),
        ("comentario no meio de expressao -> sem erro",
         ["(START)", "(5.0 *{ comentario no meio }* VAR)", "(VAR)", "(END)"],
         False),
        ("multiplos comentarios em posicoes variadas -> sem erro",
         ["(START)",
          "*{ comentario inicial }*",
          "(3 2 +) *{ resultado }*",
          "(5.0 *{ valor }* VAR)",
          "(VAR)",
          "(END)"],
         False),
        # Comentário não fechado → erro léxico → pipeline aborta (tabela is None)
        ("comentario nao fechado -> aborta",
         ["(START)", "*{ comentario aberto", "(END)"],
         True),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_abortar in casos:
        tabela, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)

        if espera_abortar:
            # Espera que o pipeline aborte (erro léxico: tabela é None)
            passou = (tabela is None)
        else:
            # Espera que o programa seja válido (sem erros semânticos)
            passou = (tabela is not None) and len(erros_decl + erros_tipo) == 0

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou and tabela is not None:
            for erro in erros_decl + erros_tipo:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def testarCasosExtremos():
    """
    Valida casos extremos: programa vazio (só START e END) e aninhamento profundo.
    Cobre até 5 níveis de aninhamento com inteiros e reais, e aninhamento com erro de tipo.
    """
    print("=" * 50)
    print("Teste: casos extremos\n")

    casos = [
        # Programa mínimo válido: apenas START e END, sem nenhuma expressão
        ("programa minimo (so START e END) -> sem erro",
         ["(START)", "(END)"], True),

        # Aninhamento de 4 níveis com inteiros
        # ((((1 2 +) 3 *) 4 -) 2 /) = ((9-4)/2) = 2
        ("aninhamento 4 niveis inteiros -> sem erro",
         ["(START)", "((((1 2 +) 3 *) 4 -) 2 /)", "(END)"], True),

        # Aninhamento de 5 níveis com inteiros
        # (((((1 2 +) 3 *) 4 -) 2 /) 3 %) = (2 % 3) = 2
        ("aninhamento 5 niveis inteiros -> sem erro",
         ["(START)", "(((((1 2 +) 3 *) 4 -) 2 /) 3 %)", "(END)"], True),

        # Aninhamento de 5 níveis com reais
        # (((((1.0 2.0 +) 3.0 *) 4.0 -) 2.0 |) 3.0 +)
        ("aninhamento 5 niveis reais -> sem erro",
         ["(START)", "(((((1.0 2.0 +) 3.0 *) 4.0 -) 2.0 |) 3.0 +)", "(END)"], True),

        # Aninhamento com bool em operação aritmética → erro semântico
        # (((1 2 <) 3 *) 4 +): (1 2 <) produz bool, bool * 3 é inválido
        ("bool em aninhamento profundo -> ERRO",
         ["(START)", "(((1 2 <) 3 *) 4 +)", "(END)"], False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, codigo, espera_valido in casos:
        _, erros_decl, erros_tipo = auxAnalisarPrograma(codigo)
        todos_erros = erros_decl + erros_tipo
        teve_erro = len(todos_erros) > 0
        passou = (espera_valido and not teve_erro) or (not espera_valido and teve_erro)

        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"

        print(f"{status} | {descricao}")
        if not passou:
            for erro in todos_erros:
                print(f"       Erro inesperado: {erro.get('mensagem', '')}")

    print(f"\nResultado: {aprovados} aprovados, {reprovados} reprovados")
    print("=" * 50 + "\n")


def iniciarTestesSemantico():
    """Executa todos os testes do analisador semantico (verificarTipos)."""
    print("\nRealizacao dos testes do analisador semantico:\n")
    testarErrosLexicos()
    testarErrosSintaticos()
    testarComentarios()
    testarCasosExtremos()
    testarLiteraisETiposBasicos()
    testarDivisaoInteiraEResto()
    testarBoolEmAritmetica()
    testarOperadoresRelacionais()
    testarCondicoesControle()
    testarExpressoesAninhadas()
    testarVariaveisMemoria()
    testarArvoreAtribuida()


if __name__ == "__main__":
    iniciarTestesSemantico()
