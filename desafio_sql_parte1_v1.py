import random
from sqlalchemy import Column, select
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DECIMAL
from sqlalchemy import BINARY
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

""""Creates a base class named Base using declarative_base from SQLAlchemy. 
This class will be used as the foundation for defining our database models 
(Cliente and Conta)."""
Base = declarative_base()


class Cliente(Base):
    """Defines a class named Cliente that inherits from the Base class.
     This class represents a customer record in the database."""

    # Specifies the name of the table that
    # will be created in the database to store customer information.
    __tablename__ = "client_perfil"

    # attributes (Columns)
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cpf = Column(String(11), nullable=False)
    address = Column(String(20))


    """
    Defines a one-to-many relationship between Cliente (customer) and Conta (account). 
    A customer can have multiple accounts, but an account belongs to one customer.
    """
    account = relationship("Conta", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Cliente (id={self.id})\nName: {self.name}\nCPF n. {self.cpf}\nAddress: {self.address}"


class Conta(Base):
    __tablename__ = "client_account"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # id = Column(BINARY, primary_key=True)
    type = Column(String, nullable=False)
    agency = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    id_client = Column(Integer, ForeignKey("client_perfil.id"), nullable=False)
    balance = Column(DECIMAL, nullable=False)

    client = relationship("Cliente", back_populates="account")

    def __repr__(self):
        return (f"Conta (id={self.id}, type={self.type}, agency={self.agency}, "
                f"number={self.number}, balance={self.balance})")


print(Cliente.__tablename__)
print(Conta.__tablename__)

# Create an instance of Engine witch connects to database SQLite.
engine = create_engine("sqlite://")

# Create all tables "Cliente" and "Conta" in the database SQLite.
Base.metadata.create_all(engine)

"""
This is a function from the sqlalchemy.inspection module. 
It provides a way to introspect a database engine or connection.
By using this code, you can effectively retrieve a list of tables 
in your database without explicitly defining them in your Python code.
"""
inspector_engine = inspect(engine)
print(inspector_engine.get_table_names())
print(inspector_engine.get_foreign_keys("client_account"))

# Sample data. List of dictionaries containing the desired attributes for each client.
client_data = [
    {"name": "João da Silva", "cpf": "12345678901", "address": "Rua A, 123"},
    {"name": "Maria Oliveira", "cpf": "98765432109", "address": "Rua B, 456"},
    {"name": "Pedro Santos", "cpf": "23456789012", "address": "Rua C, 789"},
    {"name": "Ana Costa", "cpf": "34567890123", "address": "Rua D, 1011"},
    {"name": "Carlos Pereira", "cpf": "45678901234", "address": "Rua E, 1213"},
]


# with Session(engine) as session:
#     for client_info in client_data:
#         # Create a new Cliente instance with data from the dictionary
#         novo_cliente = Cliente(
#             name=client_info["name"], cpf=client_info["cpf"], address=client_info["address"]
#         )
#         # Add the client to the session
#         session.add(novo_cliente)
#         print(novo_cliente.id)
#
#     Commit all changes at once
#     session.commit()


"""
This code snippet essentially fetches all records from the C
liente table and prints each record to the console. The session.scalars() 
method is used to efficiently retrieve the results as scalar objects, 
which are instances of the mapped class (Cliente in this case).
"""
# creates a SQLAlchemy selectable object
# representing a query to select all rows from the Cliente table.
# stmt = select(Cliente)
# session.scalars(stmt) executes the query represented by stmt
# and returns an iterable of scalar results. In this case,
# each result is an instance of the Cliente class.
# for client in session.scalars(stmt):
#     print(client.id)

account_types = ['Corrente', 'Poupança']
agencies = ['001', '002']


# Function to generate account(s) for the clients in the dictionary
def generate_account(client_id):
    return [
        {
            'type': random.choice(account_types),
            'agency': random.choice(agencies),
            'number': random.randint(100000, 999999),
            'id_client': client_id,
            'balance': round(random.uniform(100, 10000), 2)
        }
        # Creates randomly 1, 2 or 3 account for each client
        for _ in range(random.randint(1, 3))
    ]


# Create accounts for each client
with Session(engine) as session:
    for client_info in client_data:
        client = Cliente(**client_info)
        session.add(client)
        session.commit()

        account_data = generate_account(client.id)
        for account_info in account_data:
            account = Conta(**account_info)
            session.add(account)
            session.commit()

# This code creates a JOIN between Cliente and Conta based on the
# id_client foreign key, ensuring that related data is fetched together.
stmt = select(Cliente, Conta).join(Conta)

with Session(engine) as session:

    #  This line executes the query and returns a
    #  list of tuples, where each tuple contains a
    #  Conta and Cliente object.
    results = session.execute(stmt).all()

    # This iterates over the list of tuples, unpacking
    # each tuple into account and client variables.
    for client, account in results:
        print(f"{client}\n"
              f"{account}\n")


print('CPF dos clientes:')
stmt_cliente = select(Cliente)
for cliente in session.scalars(stmt_cliente):
    print(cliente.cpf)

print('Fetch conta:')
results = session.execute(select(Conta).where(Conta.id_client == 2))
print(results.fetchall())
