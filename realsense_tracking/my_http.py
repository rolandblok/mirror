from http.server import BaseHTTPRequestHandler,HTTPServer
from queue import Queue
from socketserver import ThreadingMixIn
from threading import Thread
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs
from time import perf_counter
from os import curdir, sep





use_multi_threaded_server = True
PORT_NUMBER = 8080   # local web server port number

command_queue = Queue()

class myHandler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):
        #Check the file extension required and
        #set the right mime type
        if self.path.startswith("/do_narc"):
            self.send_response(200)
            query = urlparse(self.path)
            user_data = parse_qs(query.query)
            print(user_data)
            command_queue.put(user_data['command'][0])
            pass
        else:
            try:
                sendReply = False
                if self.path.endswith(".html") or self.path == "/":
                    mimetype='text/html'
                    sendReply = True
                if self.path.endswith(".jpg"):
                    mimetype='image/jpg'
                    sendReply = True
                if self.path.endswith(".gif"):
                    mimetype='image/gif'
                    sendReply = True
                if self.path.endswith(".js"):
                    mimetype='application/javascript'
                    sendReply = True
                if self.path.endswith(".css"):
                    mimetype='text/css'
                    sendReply = True

                if sendReply == True:
                    #Open the static file requested and send it
                    file_to_send = self.path
                    if file_to_send == "/":
                        file_to_send = "index.html"
                    with open(curdir + sep + "html/" + file_to_send) as f:
                        self.send_response(200)
                        self.send_header('Content-type',mimetype)
                        self.end_headers()
                        self.wfile.write(f.read().encode("utf-8"))

            except IOError:
                self.send_error(404,'File nie gevonde nie: %s' % self.path)


class ThreadedServer(HTTPServer):
    def __init__(self):
        super().__init__(('', PORT_NUMBER), myHandler)

        self.thread = Thread(target=self.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def get_next_command(self) -> Optional[str]:
        if not command_queue.empty():
            return command_queue.get_nowait()
        return None

    def stop_server(self):
        self.socket.close()
        self.thread.join()


# if use_multi_threaded_server:
#     class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
#         pass
#     server = ThreadingSimpleServer(('', PORT_NUMBER), myHandler)
# else:
#     server = HTTPServer(('', PORT_NUMBER), myHandler)

# #Wait forever for incoming http requests
# try:
#     server.serve_forever()
# except KeyboardInterrupt:
#     print('^C received, shutting down the web server and closing database')
#     server.socket.close()
    