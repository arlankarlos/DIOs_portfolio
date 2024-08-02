import datetime
import random
from pprint import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Store connection's link to a variable
uri = "MongoDB URI"
# Create a new client and connect to the server
client_mongo = MongoClient(uri, server_api=ServerApi('1'))

# Access or create database 'desafio'
db = client_mongo.desafio
print(db)  # test purpose

# Send a ping to confirm a successful connection
try:
    client_mongo.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB")
except Exception as e:
    print(e)

# Set document
bank_client = [{
    "Nome": "Karlos",
    "CPF": "12345678910",
    "Endereço": "Goiânia/GO",
    "Data": datetime.datetime.now()
},
    {
        "Nome": "Carol",
        "CPF": "98765432110",
        "Endereço": "Trindade/GO",
        "Data": datetime.datetime.now()

    },
    # Sample list create with Gemini (made some adjustments to correct it)
    {"Nome": "Alice", "CPF": "11122233344", "Endereço": "Palmas/TO", "Data": datetime.datetime.now()},
    {"Nome": "Bruno", "CPF": "55544433322", "Endereço": "Cuiabá/MT", "Data": datetime.datetime.now()},
    {"Nome": "Débora", "CPF": "66677788899", "Endereço": "Campo Grande/MS", "Data": datetime.datetime.now()},
    {"Nome": "Enzo", "CPF": "00011122233", "Endereço": "Belém/PA", "Data": datetime.datetime.now()},
    {"Nome": "Flávia", "CPF": "77788899900", "Endereço": "Manaus/AM", "Data": datetime.datetime.now()},
    {"Nome": "Gabriel", "CPF": "88899900011", "Endereço": "Salvador/BA", "Data": datetime.datetime.now()},
    {"Nome": "Isabela", "CPF": "22233344455", "Endereço": "Fortaleza/CE", "Data": datetime.datetime.now()},
    {"Nome": "Jonas", "CPF": "33344455566", "Endereço": "Natal/RN", "Data": datetime.datetime.now()}
]

# Access or create collection 'bank_clients'
bank_clients = db.bank_clients

# Insert a document and the id at it
for client in bank_client:
    bank_client_id = bank_clients.insert_one(client).inserted_id
# print(bank_client_id) # test purpose
# print(bank_clients) # test purpose
# print(db.list_collection_names()) # test purpose

# Find documents
# for client in bank_clients.find():
#     print('{',f"'id_cliente': '{client["_id"]}'",'},')

# Find documents where clients lives in Trindade/GO
print("\nClientes residentes em Trindade/GO:")
for client in bank_clients.find():
    if client['Endereço'] == 'Trindade/GO':
        print(f"Nome: {client['Nome']} \t CPF: {client['CPF']}")


def generate_client_accounts(total_clientes):
    """Generates a list of client accounts with random data.

  Args:
    total_clientes: A Collection of existing client account dictionaries.
    total_clientes.estimated_document_count(): The number of new samples to generate.

  Returns:
    A list of new client account dictionaries.
  """

    new_accounts = []
    account_types = ["Poupança", "Conta Corrente"]  # Add more types if needed
    base_agency = "0001"  # Modify if agencies have different prefixes

    for index, document in enumerate(total_clientes.find().limit(total_clientes.estimated_document_count())):
        # Generate random data
        account_type = random.choice(account_types)
        account_number = random.randint(100000, 999999)
        id_cliente = document.get('_id')
        saldo = round(random.uniform(0, 10000))  # Random saldo between 0 and 10000

        # Create new account dictionary
        new_account = {
            "Tipo": account_type,
            "Agência": base_agency,
            "Número": account_number,
            "id_cliente": id_cliente,
            "Saldo": saldo
        }
        new_accounts.append(new_account)
    # Combine existing and new accounts
    return new_accounts


# Generate sample_accounts for the bank_clients
client_account_sample = generate_client_accounts(bank_clients)
for sample in client_account_sample:
    print(sample, ',')

# Access or create collection 'clients_accounts'
clients_accounts = db.clients_accounts

# Insert a document and the id at it
for account in client_account_sample:
    client_account_id = clients_accounts.insert_one(account).inserted_id

print("\nColeções armazenadas no mongoDB")
collections = db.list_collection_names()
for collection in collections:
    print(collection)


# Function to group (bank_clients + clients_accounts)
def get_client_account_matches(clients, accounts):
    """Validates that each account's id_cliente matches the corresponding client's _id.

  Args:
    clients: A list of client dictionaries.
    accounts: A list of account dictionaries.

  Returns:
    A list of tuples, where each tuple contains a client and its
    corresponding account if they match, or None if no match is found.
  """
    matches = []
    for client_acc in clients.find():
        for account_client in accounts.find():
            if str(account_client.get('id_cliente')) == str(client_acc.get('_id')):
                matches.append((client_acc, account_client))
                break  # Break out of the inner loop if a match is found
    return matches


# Group clients+accounts and print
matched_pairs = get_client_account_matches(bank_clients, clients_accounts)
for client in matched_pairs:
    pprint(client)
    print()

# Find a client, delete docs (client and account)
print('\nConta: Karlos\n ',
      clients_accounts.find_one({"Nome": "Karlos"}), )
karlos_id = bank_clients.find_one({"Nome": "Karlos"})
print('type:', type(bank_clients.find_one({"Nome": "Karlos"})))

# Code commented to avoid reference error
print('Karlos account n.: ',
      clients_accounts.find_one({'id_cliente': bank_clients.find_one({"Nome": "Karlos"})['_id']})['Número'])
del_account = clients_accounts.delete_one(
    {"id_cliente": bank_clients.find_one({"Nome": "Karlos"})['_id']})
del_client = bank_clients.delete_one({"Nome": "Karlos"})

# Check if the client and account were deleted
print()
print(bank_clients.find_one({"Nome": "Karlos"}))
print(clients_accounts.find_one({"id_cliente": karlos_id['_id']}))

# for client in bank_clients.find():
#     print(client['_id'])

# # Drop (delete) the collection
# result_drop_clients = db.bank_clients.drop()
result_drop_accounts = db.clients_accounts.drop()
print(db.list_collection_names())

# # Drop (delete) the database
client_mongo.drop_database('desafio')
print(db.list_collection_names())
