class BaseBackend():
    def _build_url(self, resource):
        raise NotImplementedError

    def call(self, http_method, resource, data):
        raise NotImplementedError
