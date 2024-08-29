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

caixa_banco = 10000000000
coeficiente_credito = 0.01
limite_credito = 0
credito_pessoal = 0
parcela = 0
parcelas = 0
PIX_MINIMO = 1.00
MAX_PARCELAS = 10
JUROS = 0.02

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


def filtrar_cliente(cpf, clientes):
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

def recuperar_conta_cliente(cliente, numero_conta):
    if not cliente.contas:
        print("Cliente não possui conta")
        return
    for conta in cliente.contas:
        if conta.numero == numero_conta:
            return conta

def opcao_deposito(clientes):
    cpf = input("Informe o CPF do cliente: ")
    numero_conta = int(input("Informe o número da conta: "))
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente, numero_conta)
    if not conta:
        return

    cliente.realizar_transacao(conta,transacao)


def opcao_saque(clientes):

    cpf = input("Informe o CPF do cliente: ")
    numero_conta = int(input("Informe o número da conta: "))
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente, numero_conta)
    if not conta:
        return

    cliente.realizar_transacao(conta,transacao)


def opcao_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    numero_conta = int(input("Informe o número da conta: "))
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente, numero_conta)
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


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


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
