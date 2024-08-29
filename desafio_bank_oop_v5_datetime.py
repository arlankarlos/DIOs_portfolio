from abc import ABC, abstractmethod
from datetime import datetime
import pytz
import textwrap


def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))
# def menu():
#     menu = """\n
#     ================ MENU ================

#     [c]\tCrédito Pessoal
#     [q]\tQuitar Parcela
#     [d]\tDepositar
#     [s]\tSacar
#     [e]\tExtrato
#     [n]\tNovo Cliente
#     [ln]\tListar Clientes
#     [cc]\tNova Conta Corrente
#     [lc]\tListar Contas
#     [p]\tPIX
#     [v]\tVazar
#     => """
#     return input(textwrap.dedent(menu))

caixa_banco = 10000000000
coeficiente_credito = 0.01
limite_credito = 0
credito_pessoal = 0
parcela = 0
parcelas = 0
# saldo = 0
# limite = 500
#valor = 0
#extrato = ""
# numero_saques = 0
# LIMITE_SAQUES = 3
PIX_MINIMO = 1.00
MAX_PARCELAS = 10
JUROS = 0.02
# usuarios = []
# contas_correntes = []

class Cliente:
    def __init__(self, endereco):
        self.contas = []
        self.endereco = endereco

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self,conta):
        print(*self.contas)
        self.contas.append(conta)


class Pessoa_Fisica(Cliente):
    def __init__(self, nome, data_de_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_de_nascimento = data_de_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()


    @classmethod
    def nova_conta(cls, numero, cliente ):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def agencia(self):
        return self._agencia

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Operação não realizada, valor maior que o saldo.")
        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso!")
            return True
        else:
            print("Operação não realizada.")
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Deposito realizado com sucesso.")
            return True
        else:
            print("Operação falhou.")

        return False

class Conta_Corrente(Conta):
    def __init__(self, numero, cliente, limite=1000, limite_transacoes=10):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_transacoes = limite_transacoes

    def sacar(self, valor):
        # Limite de transações diárias
        numero_transacoes = len([transacao for transacao in self.historico.transacoes if transacao['data'].date().day == datetime.now(pytz.timezone('America/Sao_Paulo')).date().day])
        # numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        excedeu_limite = valor > self.limite
        excedeu_transacoes = numero_transacoes >= self.limite_transacoes

        if excedeu_limite:
            print("Operação não realizada. Valor excede o saldo.")
        elif excedeu_transacoes:
            print("Operação não realizada. Excedeu limite de transações diárias.")
        else:
            return super().sacar(valor)

        return False

    def depositar(self, valor):
        # Limite de transações diárias
        numero_transacoes = len([transacao for transacao in self.historico.transacoes if transacao['data'].date().day == datetime.now(pytz.timezone('America/Sao_Paulo')).date().day])
        # numero_depositos = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Deposito.__name__])
        excedeu_transacoes = numero_transacoes >= self.limite_transacoes

        if excedeu_transacoes:
            print("Operação não realizada. Excedeu limite de transações diárias.")
        else:
            return super().depositar(valor)

    def __str__(self) -> str:
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            Saldo:\t\tR${self.saldo:.2f}
        """



class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @classmethod
    @abstractmethod
    def registrar(cls, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now(pytz.timezone("America/Sao_Paulo")),
        })


def filtrar_cliente(cpf, clientes, numero_conta=None):
    if numero_conta!=None:
        clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf and cliente.contas[0].numero == numero_conta]
    else:
        clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]

    return clientes_filtrados[0] if clientes_filtrados else None

def calcula_limite_credito(coeficiente_credito, limite_credito, saldo):
    limite_credito = coeficiente_credito * saldo
    limite_credito = round(limite_credito, 2)
    return limite_credito

def calcula_juros(emprestimo_desejado, parcela):
    juros = emprestimo_desejado * (JUROS*parcela)
    juros = round(juros, 2)
    return juros

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta")
        return
    # FIXME: não permite cliente escolher conta
    # print("conta recuperada")
    return cliente.contas[0]

def opcao_deposito(clientes):
    #global extrato
    #global saldo
    cpf = input("Informe o CPF do cliente: ")
    numero_conta = int(input("Informe o número da conta: "))
    cliente = filtrar_cliente(cpf, clientes, numero_conta)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta,transacao)

    # if valor > 0:
    #     saldo += valor
    #     extrato += f"Depósito: R$ {valor:.2f}\n"


    # else:
    #     print("Operação falhou! O valor informado é inválido.")
    # return saldo, extrato

def opcao_saque(clientes):
    #global saldo, extrato, numero_saques, limite, LIMITE_SAQUES
    cpf = input("Informe o CPF do cliente: ")
    numero_conta = int(input("Informe o número da conta: "))
    cliente = filtrar_cliente(cpf, clientes, numero_conta)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta,transacao)


    # excedeu_limite = valor > limite
    # excedeu_saldo = valor > saldo
    # excedeu_saques = numero_saques >= limite_saques

    # if excedeu_saldo:
    #     print("Operação falhou! Você não tem saldo suficiente.")

    # elif excedeu_limite:
    #     print("Operação falhou! O valor do saque excede o limite.")

    # elif excedeu_saques:
    #     print("Operação falhou! Número máximo de saques excedido.")

    # elif valor > 0:
    #     saldo -= valor
    #     extrato += f"Saque: R$ {valor:.2f}\n"
    #     numero_saques += 1

    # else:
    #     print("Operação falhou! O valor informado é inválido.")
    # return saldo, extrato, numero_saques

# def opcao_pix():
#     global saldo, PIX_MINIMO, extrato
#     valor = float(input("Informe o valor para o PIX: "))
#     beneficiario = input("Informe o nome do beneficiário: ")

#     excedeu_saldo = valor > saldo
#     minimo_pix = valor >= PIX_MINIMO

#     if excedeu_saldo:
#         print("Operação falhou! Você não tem saldo suficiente.")
#     elif not minimo_pix:
#         print("Operação falhou! O valor do PIX é inválido.")
#     elif valor > 0 and minimo_pix:
#         saldo -= valor
#         extrato += f"PIX: -R$ {valor:.2f} p/ '{beneficiario.upper()}'\n"
#         print("Operação realizada com sucesso!")
    # else:
    #     print("Operação falhou! O valor informado é inválido.")

# def opcao_credito_pessoal():
#     global parcelas, limite_credito, saldo, credito_pessoal, extrato, parcela

#     print(f"Crédito Pessoal disponível (só 2% ao mês): R$ {limite_credito:.2f}")
#     valor = float(input("Informe o valor do crédito desejado: "))
#     parcelas = int(input("Informe a quantidade de parcelas (até 10): "))

#     excedeu_limite = valor > limite_credito
#     if excedeu_limite:
#         print("Operação falhou! O valor do crédito excede o limite.")


#     elif valor > 0:
#         credito_pessoal = valor + calcula_juros(valor, parcelas)
#         parcela = credito_pessoal / parcelas
#         parcela = round(parcela, 2)
#         print(f"Parcela de R$ {parcela:.2f} em {parcelas}x (2% a.m.)")
#         print(f"Total: R$ {credito_pessoal:.2f}")
#         confirmacao = input("Deseja confirmar o crédito? (S/N): ")

#         if confirmacao.upper() == "S":
#             limite_credito -= valor
#             saldo += valor

#             extrato += f"Crédito Pessoal: R$ {valor:.2f}\n"
#             print("Operação realizada com sucesso!")
#         else:
#             credito_pessoal = 0
#             parcelas = 0
#             parcela = 0
#             print("Operação cancelada.")
#     else:
#         print("Operação falhou! O valor informado é inválido.")

# def opcao_quitar_parcela():
#     global saldo, parcela, credito_pessoal, parcelas, extrato
#     print(f"Crédito Pessoal Contratado: {credito_pessoal}")
#     print(f"Parcelas: {parcelas}")
#     decisao = input(f"Quitar R$ {parcela}? (S/N) ")

#     excedeu_saldo = parcela > saldo


#     if excedeu_saldo:
#         print("Operação falhou! Você não tem saldo suficiente.")



#     elif decisao.upper() == "S":
#         credito_pessoal -= parcela
#         saldo -= parcela
#         parcelas -= 1
#         extrato += f"Pagamento CP: -R$ {parcela:.2f}\n"
#         print("Operação realizada com sucesso!")


#         if parcelas == 0:
#             print("Crédito Pessoal Finalizado")
#             credito_pessoal = 0
#             parcela = 0

#     else:
#         print("Operação cancelada.")

def opcao_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    numero_conta = int(input("Informe o número da conta: "))
    cliente = filtrar_cliente(cpf, clientes, numero_conta)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""

    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['data'].strftime("%d/%m/%Y %H:%M")} - {transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


    # global limite_credito
    # global credito_pessoal
    # print("\n================ EXTRATO ================")
    # print("Não foram realizadas movimentações." if not extrato else extrato)
    # print(f"\nSaldo: R$ {saldo:.2f}")
    # print("==========================================\n\n")
    # print("==========CRÉDITO DISPONÍVEL===============")
    # print(f"Crédito disponível: R$ {limite_credito:.2f}")
    # print("==========================================\n\n")
    # print("==========CRÉDITO CONTRATADO===============")
    # print(f"Crédito contratado: R$ {credito_pessoal:.2f}")
    # print("==========================================")

def criar_usuario(clientes):

    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n Cliente já existente.")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, n., bairro, cidade/UF): ")

    cliente = Pessoa_Fisica(nome=nome, data_de_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n Cliente criado com sucesso!")
    # CPF = int(input("CPF: "))
    # existente = False
    # for usuario in usuarios:
    #     if usuario['CPF'] == CPF:
    #         existente = True
    # if existente:
    #     print("Cliente existente, abra uma conta.")
    # else:
    #     novo_usuario = {}
    #     novo_usuario["CPF"] = CPF
    #     novo_usuario["Nome"] = input('Nome: ')
    #     novo_usuario["Data de nascimento"] = input('Data de nascimento (dd/mm/aaaa): ')
    #     print("Endereço completo")
    #     novo_usuario["Endereço"] = input("Logradouro: ") + ', ' + input("Número: ") + ', ' + input("Bairro: ") + ', ' + input("Cidade: ") + "/" + input("UF: ")
    #     usuarios.append(novo_usuario)
    #     print('Novo cliente adicionado com sucesso')
    # return usuarios

def listar_clientes(usuarios):
    for usuario in usuarios:
        print(f"CPF: {usuario['CPF']}         Cliente: {usuario['Nome']}")
        print("==========================================")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    conta = Conta_Corrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\nConta Criada com sucesso!")
# def nova_conta_corrente(contas_correntes, usuarios):

#     nome = input('Nome do(a) cliente: ')
#     CPF = int(input("CPF: "))
#     existente = True
#     for usuario in usuarios:
#         if usuario['CPF'] == CPF:
#             existente = False
#     if existente:
#         print("Primeiro cadastre o cliente, cliente inexistente.")
#     else:
#         nova_conta_corrente = {}
#         nova_conta_corrente["Agência"] = '0001'
#         nova_conta_corrente['Número da conta'] = len(contas_correntes)+1
#         nova_conta_corrente['Usuário'] = CPF
#         print(f'Conta criada com sucesso!!!\nConta número: {nova_conta_corrente['Número da conta']} criada para o(a) cliente {nome.upper()}.')
#         contas_correntes.append(nova_conta_corrente)

#     return contas_correntes

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

    # for conta in contas_correntes:
    #     print(conta)
    #     print("==========================================")


def main():

    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            opcao_deposito(clientes)

        elif opcao == "s":
            opcao_saque(clientes)

        elif opcao == "e":
            opcao_extrato(clientes)

        elif opcao == "nu":
            criar_usuario(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

main()
# while True:

#     opcao = input(menu)
#     limite_credito = (calcula_limite_credito(coeficiente_credito, limite_credito, saldo))-credito_pessoal
#     #Deposito
#     if opcao == "d":
#         saldo, extrato = opcao_deposito(saldo, extrato, valor)

#     # Saque
#     elif opcao == "s":
#         valor = float(input("Informe o valor do saque: "))
#         if numero_saques < LIMITE_SAQUES:

#             saldo, extrato, numero_saques = opcao_saque(saldo=saldo, valor=valor, extrato=extrato, numero_saques=numero_saques, limite=limite, limite_saques=LIMITE_SAQUES)

#     # Inclusão opção PIX e beneficiário
#     elif opcao == "p":
#         opcao_pix()

#     # Inclusão Crédito Pessoal
#     elif opcao == "c":
#         if limite_credito < 0:
#             print("Limite de Crédito Pessoal Insuficiente")
#             continue
#         else:
#             opcao_credito_pessoal()

#     #Quitar Parcela do Crédito Pessoal
#     elif opcao == "q":
#         if parcelas > 0:
#             opcao_quitar_parcela()
#         else:
#             print('Não deve parcelas, contrate agora seu crédito.')

#     # Extrato
#     elif opcao == "e":
#         opcao_extrato(saldo, extrato=extrato)

#     # Sair
#     elif opcao == "v":
#         break
#     # Novo Cliente
#     elif opcao == "n":
#         usuarios = criar_usuario(usuarios)

#     elif opcao == "ln":
#         listar_clientes(usuarios)
#     # Nova Conta Corrente
#     elif opcao == "cc":
#         nova_conta_corrente(contas_correntes,usuarios)
#     elif opcao == "lc":
#         listar_contas_correntes(contas_correntes)
#     # Opção inválida
#     else:
#         print("Operação inválida, por favor selecione novamente a operação desejada.")

