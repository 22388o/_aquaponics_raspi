from http.server import HTTPServer, BaseHTTPRequestHandler  # two necessary modules to run the web server
import cgi
import urllib

class AquaponicsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        croppedpath = self.path[1:]
        try:
            # Check the file extension required and
            # set the right mime type

            send_reply = False

            extension = self.path.split(".")[-1]
            mime_types = {'html':       'text/html',
                          'jpg':        'image/jpg',
                          'gif':        'image/gif',
                          'js':         'application/javascript',
                          'css':        'text/css',
                          'pdf':        'application/pdf',
                          'txt':        'text/txt',
                          'acsiidoc':   'text/txt'}

            mimetype = mime_types.get(extension)
            if mimetype is None:
                send_reply = False
            else:
                send_reply = True

            if send_reply:
                # Open the static file requested and send it
                if mimetype in ['text/html', 'text/css', 'text/txt']:
                    file_to_open = open(croppedpath).read()
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(bytes(file_to_open, 'utf-8'))
                elif mimetype in ['image/jpg', 'application/pdf']:
                    with open(croppedpath, 'rb') as file:
                        self.send_response(200)
                        self.send_header('Content-type', mimetype)
                        self.end_headers()
                        self.wfile.write(file.read())


        # self.send_header('content-type', 'text/html')

        except:
            file_to_open = "Pick an other file please!"
            self.send_response(404)

    def do_POST(self):
        if self.path == "/contact.html":
            croppedpath = self.path[1:]
            print(croppedpath)
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            print("ctype: {}\npdict: {}".format(ctype, pdict))
            if ctype == 'multipart/form-data':
                postvars = cgi. parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])

                print(length)
                A = self.rfile.read(length)
                print(A)
                print("---")

                postvars = urllib.parse.parse_qs(bytes.decode(A, 'ascii'), keep_blank_values=1)
            else:
                postvars = {}
            print(postvars)

            file_to_open = open("contact-sent.html").read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))



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
