from pymongo import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus, urlsplit, urlunsplit
from app.core.config import MONGO_URL


def escape_mongo_credentials(url: str) -> str:
    """Escape MongoDB user/password if necessary without failing on malformed URLs."""
    if not url or "@" not in url:
        return url

    try:
        parsed = urlsplit(url)
    except ValueError:
        return url

    if not parsed.username and not parsed.password:
        return url

    try:
        username = quote_plus(parsed.username) if parsed.username else ""
        password = quote_plus(parsed.password) if parsed.password else ""
        host = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        netloc = f"{username}:{password}@{host}{port}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    except ValueError:
        return url


class LazyMongoCollection:
    def __init__(self, db_proxy: "LazyMongoDatabase", name: str):
        self._db_proxy = db_proxy
        self._name = name
        self._collection = None

    def _resolve(self):
        if self._collection is None:
            self._collection = self._db_proxy._connect()[self._name]
        return self._collection

    def __getattr__(self, item):
        return getattr(self._resolve(), item)

    def __iter__(self):
        return iter(self._resolve())


class LazyMongoDatabase:
    def __init__(self, url: str, db_name: str = "rural"):
        self._url = url
        self._db_name = db_name
        self._client = None
        self._database = None

    def _connect(self):
        if self._database is None:
            if not self._url:
                raise RuntimeError(
                    "MONGO_URL is not configured. Please set the MONGO_URL environment variable."
                )

            try:
                self._client = MongoClient(self._url, server_api=ServerApi("1"))
            except Exception as exc:
                escaped_url = escape_mongo_credentials(self._url)
                if escaped_url != self._url:
                    try:
                        self._client = MongoClient(escaped_url, server_api=ServerApi("1"))
                    except Exception:
                        raise RuntimeError(
                            f"Failed to initialize MongoDB client from MONGO_URL: {exc}"
                        ) from exc
                else:
                    raise RuntimeError(
                        f"Failed to initialize MongoDB client from MONGO_URL: {exc}"
                    ) from exc

            self._database = self._client[self._db_name]
        return self._database

    def __getitem__(self, name):
        return LazyMongoCollection(self, name)

    def __getattr__(self, name):
        return getattr(self._connect(), name)


# Cria a conexão apenas na primeira operação de banco
# Isso evita falhas de importação global em ambientes serverless.
db = LazyMongoDatabase(MONGO_URL)
