# Trey Rubino

import json

class CustomProtocol:
    def validate(self):
        raise NotImplementedError("Subclass must implement `validate`.")

    def prepare(self) -> bytes:
        self.validate()
        return self.encode()

    def encode(self) -> bytes:
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False).encode('utf-8')

    @staticmethod
    def decode(data: bytes, cls):
        raw_data = json.loads(data.decode('utf-8'))
        return cls(**raw_data)

    def attach_binary_data(self, binary_data: bytes):
        if hasattr(self, 'size') and len(binary_data) == self.size:
            self.binary_data = binary_data
        else:
            raise ValueError(f"Binary data size mismatch. Expected {self.size}, got {len(binary_data)}.")

    def get_binary_data(self) -> bytes:
        return getattr(self, 'binary_data', b"")