import datetime
from pprint import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Store connection's link to a variable
uri = "mongodb+srv://prfakgn:PlDBvPL33NSse0vc@dio-python-dev.m7yfofn.mongodb.net/?retryWrites=true&w=majority&appName=DIO-Python-Dev"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB")
except Exception as e:
    print(e)

# Access or create database 'desafio'
db = client.desafio


collection = db.desafio_collection
# print(db) # test purpose
# print(collection) # test purpose


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
for client in bank_clients.find():
    print('Happy: ',client)

# Find documents where clients lives in Trindade/GO
print("\nClientes residentes em Trindade/GO:")
for client in bank_clients.find():
    if client['Endereço'] == 'Trindade/GO':
        print(f"Nome: {client['Nome']} \t CPF: {client['CPF']}")