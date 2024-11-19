import json

# abstract
class Protocol:
    size: float

    def validate(self):
        raise NotImplementedError("Subclass must implement `validate`.")

    def prepare(self) -> bytes:
        self.validate
        return self.encode()
    
    def encode(self) -> bytes:
        return json.dumps(self, default = lambda o: o.__dict__, ensure_ascii = False).encode('utf-8')
    
    def decode(data: bytes, cls):
        raw_data = json.loads(data)
        return cls(**raw_data)