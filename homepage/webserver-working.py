from http.server import HTTPServer, BaseHTTPRequestHandler  # two necessary modules to run the web server

class AquaponicsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)

        # self.send_header('content-type', 'text/html')

        except:
            file_to_open = "Pick an other file please!"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
        #
        # content = self.path[1:]
        # op, msg = content.split(sep="==")[0], content.split(sep="==")[-1]
        #
        # print("op: {}".format(op))
        # print("msg: {}".format(msg))
        #
        # if op == "DO":
        #     switch = {'on': 'Turned_ON', 'off': 'Turned_Off'}
        #
        #     self.send_response(200)
        #
        # elif op in ["DOC", "DOCU", "DOCUMENT"]:
        #     doc_to_open = open("/home/pi/python_projects/Aquaponics/documentation/{}".format(msg)).read()
        #     self.wfile.write(bytes(doc_to_open, 'utf-8'))
        #     self.send_response(200)
        #
        # elif op == "REN":
        #     display_8x8.display_8x8(string=msg, char="@", charset=None)
        #
        # elif op == "FILE":
        #     data = FiRO.txt_read_in(file="/home/pi/python_projects/Aquaponics/documentation/ch01.asciidoc", logical=True, nullbyte=False)
        #     for _ in data:
        #         self.wfile.write(bytes("{}".format(_), 'utf-8'))

        # if self.path == '/':
        #     self.path = '/index.html'
        #     runtest.m1()
        # try:
        #     file_to_open = open(self.path[1:]).read()
        #
        #
        # except:
        #     file_to_open = "FCKIT!!! File not found"
        #     self.send_response(404)


def ws(server_ip: str = "", port: int = 8042,):
    """=== Function name: ws ===========================================================================================
    running a webserver
    :param port:
    :param server_ip:
    :return:
    ============================================================================================== by Sziller ==="""
    if not server_ip:
        server_ip = socket.gethostbyname(socket.gethostname())
    address = (server_ip, port)
    server = HTTPServer(address, AquaponicsHandler)
    print("server running on ip     : {}".format(server_ip))
    print("server running on port   : {}".format(port))
    server.serve_forever()


if __name__ == "__main__":
    ws(port=80, server_ip='127.0.0.1')
