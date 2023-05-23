from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
        
    def adicionar_conta(self, conta):
        self.contas.append(conta)
    
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        conta = cls(numero, cliente)
        cliente.adicionar_conta(conta)
        return conta
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia

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
            print("\nOperação falhou! \nSaldo insuficiente!")
        
        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True
            
        else:
            print("\nOperação falhou! \nValor inválido!")
    
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
        else:
            print("\nOperação falhou! \nValor inválido!")
        
            return False
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )
        
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques
        
        if excedeu_limite:
            print("\nOperação falhou! \nO valor do saque excede o limite!")
            
        elif excedeu_saques:
            print("\nOperação falhou! \nNúmero máximo de saques excedido.")

        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            Conta:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
        
class Historico:
    def __init__(self):
        self._transacoes = []
        
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
    
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self, conta):
        pass
    
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
            
def menu():
    menu ="""\n
    [1] \t --> Depositar
    [2] \t --> Sacar
    [3] \t --> Extrato
    [4] \t --> Novo cliente
    [5] \t --> Nova conta
    [6] \t --> Listar contas
    [7] \t --> Sair
    """
    return input(menu)

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if cliente.contas:
        return cliente.contas[0]
    else:
        print("O cliente não possui contas associadas!")
        return None

def depositar(saldo, deposito, extrato):
    if deposito > 0:
        saldo += deposito
        
        print(f"Você depositou R${deposito}! \n")
        extrato += (f"Você depositou R${deposito}! \n")
    else:
        print("\nOperação falhou! \nValor inválido!")
    
    return saldo, extrato

def sacar(saldo, saque, extrato, limite, numero_saques, limite_saques):
    if saque > saldo:
        print("\nOperação falhou! \nSaldo insuficiente!")
        
    elif saque > limite:
        print("\nOperação falhou! \nLimite excedido!")
    
    elif numero_saques >= limite_saques:
        print("\nOperação falhou! \nNúmero máximo de saques excedido!")
    
    elif saque > 0:
        saldo -= saque
        
        print(f"Você sacou R${saque}! \n")
        extrato += (f"Você sacou R${saque}! \n")
                
        numero_saques += 1
        
        print(numero_saques, limite_saques)
        
    else:
        print("\nOperação falhou! \nValor inválido!")
    
    return saldo, extrato

def ver_extrato(clientes):
    cpf = int(input("Informe o CPF do cliente: "))
    cliente = filtrar_cliente(cpf, clientes)
    
    if not cliente:
        print("Cliente não encontrado! ")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    extrato = conta.historico.transacoes
    if not extrato:
        print("Não foram encontradas transações!")
    else:
        for transacao in extrato:
            print(f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}")
    
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def novo_cliente(clientes):
    cpf = int(input("Informe seu CPF (somente números): \n"))
    cliente = checar_cliente(cpf, clientes)
    
    if not cliente:
        nome = input("Informe seu nome completo: \n")
        data_nascimento = input("Informe sua data de nascimento (dd-mm-aaaa): \n")
        endereco = input("Informe o seu endereço: (logadouro, número, bairro, cidade/sigla estado: \n")
        
        clientes.append(PessoaFisica(nome, data_nascimento, cpf, endereco))
        
        print("\nUsuário criado com sucesso!\n")
    else:
        print("Já existe um usuário com esse CPF!")
        return

def checar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None
    
def nova_conta(numero_conta, clientes, contas):
    cpf = int(input("Informe seu CPF (somente números): \n"))
    cliente = checar_cliente(cpf, clientes)

    if cliente:
        conta = ContaCorrente.nova_conta(cliente, numero_conta)
        cliente.adicionar_conta(conta)
        contas.append(conta)
        print("\nConta criada com sucesso!\n")
    else:
        print("Usuário não encontrado! \n")

def listar_contas(contas):
    for conta in contas:
        linha = f"""\
            Agência:\t{conta.agencia}
            Conta:\t{conta.numero}
            Titular:\t{conta.cliente.nome}
        """
        print(linha)

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            cpf = int(input("Informe o CPF do cliente: "))
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("Cliente não encontrado! ")
            else:
                conta = recuperar_conta_cliente(cliente)
                if conta:
                    valor = float(input("Informe o valor a ser depositado: "))
                    deposito = Deposito(valor)
                    cliente.realizar_transacao(conta, deposito)

        elif opcao == "2":
            cpf = int(input("Informe o CPF do cliente: "))
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("Cliente não encontrado! ")
            else:
                conta = recuperar_conta_cliente(cliente)
                if conta:
                    valor = float(input("Informe o valor a ser sacado: "))
                    saque = Saque(valor)
                    cliente.realizar_transacao(conta, saque)

        elif opcao == "3":
            ver_extrato(clientes)

        elif opcao == "4":
            novo_cliente(clientes)

        elif opcao == "5":
            numero_conta = len(contas) + 1
            nova_conta(numero_conta, clientes, contas)

        elif opcao == "6":
            listar_contas(contas)

        elif opcao == "7":
            print("Obrigado por utilizar nosso sistema!")
            break

        else:
            print("Opção inválida! ")

if __name__ == "__main__":
    main()
