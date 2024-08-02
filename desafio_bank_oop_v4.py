menu = """

[c] Crédito Pessoal
[q] Quitar Parcela
[d] Depositar
[s] Sacar
[e] Extrato
[p] PIX
[v] Vazar

=> """

caixa_banco = 10000000000
coeficiente_credito = 0.01
limite_credito = 0
credito_pessoal = 0
parcela = 0
parcelas = 0
saldo = 0
limite = 500
valor = 0
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3
PIX_MINIMO = 1.00
MAX_PARCELAS = 10
JUROS = 0.02

def calcula_limite_credito(coeficiente_credito, limite_credito, saldo):
  limite_credito = coeficiente_credito * saldo
  limite_credito = round(limite_credito, 2)
  return limite_credito

def calcula_juros(emprestimo_desejado, parcela):
  juros = emprestimo_desejado * (JUROS*parcela)
  juros = round(juros, 2)
  return juros

def opcao_deposito():
    global extrato
    global saldo
    valor = float(input("Informe o valor do depósito: "))

    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"

    else:
        print("Operação falhou! O valor informado é inválido.")

def opcao_saque(saldo=saldo, valor=valor, extrato=extrato, limite=limite, numero_saques=numero_saques, LIMITE_SAQUES=LIMITE_SAQUES):
    #global saldo, extrato, numero_saques, limite, LIMITE_SAQUES
    valor = float(input("Informe o valor do saque: "))

    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= LIMITE_SAQUES

    if excedeu_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")

    elif excedeu_limite:
        print("Operação falhou! O valor do saque excede o limite.")

    elif excedeu_saques:
        print("Operação falhou! Número máximo de saques excedido.")

    elif valor > 0:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        print("Saque realizado")
        

    else:
        print("Operação falhou! O valor informado é inválido.")

def opcao_pix():
    global saldo, PIX_MINIMO, extrato
    valor = float(input("Informe o valor para o PIX: "))
    beneficiario = input("Informe o nome do beneficiário: ")

    excedeu_saldo = valor > saldo
    minimo_pix = valor >= PIX_MINIMO

    if excedeu_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
    elif not minimo_pix:
        print("Operação falhou! O valor do PIX é inválido.")
    elif valor > 0 and minimo_pix:
        saldo -= valor
        extrato += f"PIX: -R$ {valor:.2f} p/ '{beneficiario.upper()}'\n"
        print("Operação realizada com sucesso!")
    else:
        print("Operação falhou! O valor informado é inválido.")

def opcao_credito_pessoal():
    global parcelas, limite_credito, saldo, credito_pessoal, extrato, parcela
    
    print(f"Crédito Pessoal disponível (só 2% ao mês): R$ {limite_credito:.2f}")
    valor = float(input("Informe o valor do crédito desejado: "))
    parcelas = int(input("Informe a quantidade de parcelas (até 10): "))

    excedeu_limite = valor > limite_credito
    if excedeu_limite:
        print("Operação falhou! O valor do crédito excede o limite.")
    
            
    elif valor > 0:
        credito_pessoal = valor + calcula_juros(valor, parcelas)
        parcela = credito_pessoal / parcelas
        parcela = round(parcela, 2)
        print(f"Parcela de R$ {parcela:.2f} em {parcelas}x (2% a.m.)")
        print(f"Total: R$ {credito_pessoal:.2f}")
        confirmacao = input("Deseja confirmar o crédito? (S/N): ")

        if confirmacao.upper() == "S":
            limite_credito -= valor
            saldo += valor
            
            extrato += f"Crédito Pessoal: R$ {valor:.2f}\n"
            print("Operação realizada com sucesso!")
        else:
            credito_pessoal = 0
            parcelas = 0
            parcela = 0
            print("Operação cancelada.")
    else:
        print("Operação falhou! O valor informado é inválido.")

def opcao_quitar_parcela():
    global saldo, parcela, credito_pessoal, parcelas, extrato
    print(f"Crédito Pessoal Contratado: {credito_pessoal}")
    print(f"Parcelas: {parcelas}")
    decisao = input(f"Quitar R$ {parcela}? (S/N) ")

    excedeu_saldo = parcela > saldo


    if excedeu_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")

    

    elif decisao.upper() == "S":
        credito_pessoal -= parcela
        saldo -= parcela
        parcelas -= 1
        extrato += f"Pagamento CP: -R$ {parcela:.2f}\n"
        print("Operação realizada com sucesso!")
        

        if parcelas == 0:
            print("Crédito Pessoal Finalizado")
            credito_pessoal = 0
            parcela = 0

    else:
        print("Operação cancelada.")

def opcao_extrato():

    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================\n\n")
    print("==========CRÉDITO DISPONÍVEL===============")
    print(f"Crédito disponível: R$ {limite_credito:.2f}")
    print("==========================================\n\n")
    print("==========CRÉDITO CONTRATADO===============")
    print(f"Crédito contratado: R$ {credito_pessoal:.2f}")
    print("==========================================")

while True:

    opcao = input(menu)
    limite_credito = (calcula_limite_credito(coeficiente_credito, limite_credito, saldo))-credito_pessoal
    #Deposito
    if opcao == "d":
        opcao_deposito()

    # Saque
    elif opcao == "s":
        opcao_saque(saldo,valor,extrato,limite,numero_saques,LIMITE_SAQUES)

    # Inclusão opção PIX e beneficiário
    elif opcao == "p":
        opcao_pix()

    # Inclusão Crédito Pessoal
    elif opcao == "c":
        if limite_credito < 0:
            print("Limite de Crédito Pessoal Insuficiente") 
            continue
        else:
            opcao_credito_pessoal()

    #Quitar Parcela do Crédito Pessoal
    elif opcao == "q":
        if parcelas > 0:
            opcao_quitar_parcela()
        else:
            print('Não deve parcelas, contrate agora seu crédito.')

    # Extrato            
    elif opcao == "e":
        opcao_extrato()

    # Sair
    elif opcao == "v":
        break
    
    # Opção inválida
    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")
