# Trey Rubino

# `Abstract` class of our custom  protocol.
# Both `Request` and `Response` inherit the methods in this class (they are derived classes).
# CustomProtocol handles the preparation, altering, validating, and decoding our communications.
# This design allows growth in this project allowing others build other types of request and response,
# in a `Polymorphic` way. This would be ideal if we wanted to add in more functionality at a later data.

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