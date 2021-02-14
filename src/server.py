from Classes.Config import Config
import socket


HOST = '127.0.0.1'
PORT = 65432

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if data:
                    break
            conn.send(b'Successfully Received Configuration!')
            config = Config(eval(data.decode()))
            config.verify(server=True, socket=conn)