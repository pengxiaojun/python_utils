#!/usr/bin/python
# -*-coding: utf-8 -*-


from BaseHTTPServer import BaseHTTPRequestHandler
import cgi
import sys
import os


class PostHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        self.send_header("CONTENT_TYPE", "application/json;charset=utf-8")
        self.end_headers()
        # self.wfile.write('Client: %s\n' % str(self.client_address))
        # self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        # self.wfile.write('Path: %s\n' % self.path)
        # self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # handle file upload from IE. We only need file name
                filename = field_item.filename
                slash = field_item.filename.rfind('\\')
                if slash != -1:
                    filename = filename[slash+1:]

                filename = os.path.join(store_path, filename)
                partialname = filename + ".part"

                # The field contains an uploaded file
                save_file = open(partialname, "wb")
                file_len = 0

                while True:
                    file_data = field_item.file.read(8192)
                    if not file_data:
                        break
                    file_len += len(file_data)
                    save_file.write(file_data)
                    del file_data

                save_file.close()
                os.rename(partialname, filename)

                # file_data = field_item.file.read()
                # file_len = len(file_data)

                self.wfile.write('{"ret":0,"file":"%s","size":%d}' %
                                 (field_item.filename, file_len))
            else:
                pass
                # Regular form value
                # self.wfile.write('\t%s=%s\n' % (field, form[field].value))
        return


if __name__ == '__main__':
    store_path = ''
    if len(sys.argv) > 1:
        store_path = sys.argv[1]

    if store_path != '' and not os.path.exists(store_path):
        print('Path %s not exists' % store_path)
        sys.exit(0)

    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('0.0.0.0', 12323), PostHandler)
    print('File store path: %s' % store_path)
    print('Start upload server, use <Ctrl-C> to stop')
    server.serve_forever()
