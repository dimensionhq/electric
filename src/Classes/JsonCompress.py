import gzip
from io import BytesIO, TextIOWrapper

class JSONCompress():
    @staticmethod
    def load_compressed_file(f: TextIOWrapper):
        data = f.read()
        bio = BytesIO()
        stream = BytesIO(data)
        decompressor = gzip.GzipFile(fileobj=stream, mode='r')
        while True:  # until EOF
            chunk = decompressor.read(8192)
            if not chunk:
                decompressor.close()
                bio.seek(0)
                return bio.read().decode("utf-8")
            bio.write(chunk)

    @staticmethod
    def compress_json_to_bytes(input_string: str) -> bytes:
        """
        read the given string, encode it in utf-8,
        compress the data and return it as a byte array.
        """
        bio = BytesIO()
        bio.write(input_string.encode("utf-8"))
        bio.seek(0)
        stream = BytesIO()
        compressor = gzip.GzipFile(fileobj=stream, mode='w')
        while True:  # until EOF
            chunk = bio.read(8192)
            if not chunk:  # EOF?
                compressor.close()
                return stream.getvalue()
            compressor.write(chunk)
