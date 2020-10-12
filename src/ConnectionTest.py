import socket
import speedtest


def test_connection(self):
    try:
        socket.create_connection(('Google.com', 80))
        return True
    except OSError:
        return False


def test_speed(self):
    sp = speedtest.Speedtest()
    return sp.download()
