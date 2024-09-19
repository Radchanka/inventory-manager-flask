import os
import subprocess
import time
import webbrowser

FLASK_APP_PATH = 'D:\\Inventory Manager\\app.py'

PYTHON_PATH = 'D:\\Inventory Manager\\venv\\Scripts\\python.exe'

WORKING_DIR = os.path.dirname(FLASK_APP_PATH)

server_process = subprocess.Popen([PYTHON_PATH, FLASK_APP_PATH], cwd=WORKING_DIR,
                                  creationflags=subprocess.CREATE_NO_WINDOW)

time.sleep(10)

webbrowser.open('http://127.0.0.1:5000')

print("Server started. Browser opened.")
