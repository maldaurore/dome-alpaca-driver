import tkinter as tk
from flask import Flask, jsonify
import threading
from routes import setup_route
from gui import DomoControllerApp

# Crear una instancia de Flask
app = Flask(__name__)

setup_route(app)

# Función para ejecutar el servidor Flask en un hilo separado
def run_server():
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    # Ejecutar el servidor HTTP en un hilo separado
    threading.Thread(target=run_server, daemon=True).start()

    # Crear y mostrar la GUI
    root = tk.Tk()
    app = DomoControllerApp(root)
    root.mainloop()
