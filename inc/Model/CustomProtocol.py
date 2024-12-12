# Trey Rubino

import json

class CustomProtocol:
    """
    Abstract base class for the custom protocol.

    This class defines shared behavior for `Request` and `Response` objects, 
    including preparation, encoding, decoding, validation, and binary data handling.

    Methods:
        validate(): Abstract method for validation, to be implemented by subclasses.
        prepare() -> bytes: Validates the instance and encodes it into bytes for transmission.
        encode() -> bytes: Encodes the instance as a JSON-formatted byte string.
        decode(data: bytes, cls): Decodes a JSON-formatted byte string into an instance of the specified class.
        attach_binary_data(binary_data: bytes): Attaches binary data to the instance, ensuring size consistency.
        get_binary_data() -> bytes: Retrieves attached binary data, if any.
    """

    def validate(self):
        """
        Abstract method for validation.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclass must implement `validate`.")

    def prepare(self) -> bytes:
        """
        Validates the instance and encodes it into bytes for transmission.

        Returns:
            bytes: The JSON-encoded byte representation of the instance.
        """
        self.validate()
        return self.encode()

    def encode(self) -> bytes:
        """
        Encodes the instance as a JSON-formatted byte string.

        Returns:
            bytes: The JSON-encoded byte representation of the instance.
        """
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False).encode('utf-8')

    @staticmethod
    def decode(data: bytes, cls):
        """
        Decodes a JSON-formatted byte string into an instance of the specified class.

        Args:
            data (bytes): The JSON-formatted byte string to decode.
            cls: The class to instantiate with the parsed data.

        Returns:
            An instance of the specified class.

        Raises:
            Exception: If there is an error during decoding or instantiation.
        """
        # Decode the bytes to a string and parse the JSON data
        raw_data = json.loads(data.decode('utf-8'))

        # Handle the conversion of dictionaries in 'contents' to Content objects
        if 'contents' in raw_data:
            from .Response import Content  # Dynamically import Content
            try:
                raw_data['contents'] = [Content(**item) for item in raw_data['contents']]
            except Exception as e:
                print("Error converting 'contents' to Content objects:", e)  # Debug: Show conversion error

        # Create an instance of the class with the parsed data
        try:
            return cls(**raw_data)
        except Exception as e:
            print(f"Error creating instance of '{cls.__name__}':", e)  # Debug: Show instantiation error
            raise

    def attach_binary_data(self, binary_data: bytes):
        """
        Attaches binary data to the instance, ensuring size consistency.

        Args:
            binary_data (bytes): The binary data to attach.

        Raises:
            ValueError: If the size of the binary data does not match the expected size.
        """
        if hasattr(self, 'size') and len(binary_data) == self.size:
            self.binary_data = binary_data
        else:
            raise ValueError(f"Binary data size mismatch. Expected {self.size}, got {len(binary_data)}.")

    def get_binary_data(self) -> bytes:
        """
        Retrieves attached binary data, if any.

        Returns:
            bytes: The attached binary data, or an empty byte string if no data is attached.
        """
        return getattr(self, 'binary_data', b"")
