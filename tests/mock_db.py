class DummyDB:
    def ejecutar_query(self, query, params=None):
        return []
    def ejecutar_query_return_rowcount(self, query, params=None):
        return 1
    def conectar(self):
        pass
    @property
    def connection(self):
        return None
