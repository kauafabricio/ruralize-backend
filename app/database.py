from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from pymongo.server_api import ServerApi
from app.core.config import MONGO_URL, MONGO_DB_NAME

# cria a conexão com timeouts curtos para evitar travar requisições quando o Mongo não estiver disponível
client = MongoClient(
    MONGO_URL,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=3000,
    connectTimeoutMS=3000,
)

# seleciona o banco padrão definido na URL ou utiliza a variável de ambiente
try:
    db = client.get_default_database()
except ConfigurationError:
    db = client[MONGO_DB_NAME]

if db is None:
    db = client[MONGO_DB_NAME]
