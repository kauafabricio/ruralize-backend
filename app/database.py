from pymongo import MongoClient
from pymongo.server_api import ServerApi
from app.core.config import MONGO_URL

# cria a conexão
client = MongoClient(MONGO_URL, server_api=ServerApi('1'))

# seleciona o banco
db = client["rural"]
