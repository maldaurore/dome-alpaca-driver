import tkinter as tk
from tkinter import messagebox
import requests

class DomoControllerApp:
  def __init__(self, root):
    self.root = root
    self.root.title("Controlador de Domo ASCOM Alpaca")
    self.root.geometry("400x800")

    self.server_address = "http://localhost:5000"
    self.transaction_id = 0
        
    # Mensaje principal
    self.title_label = tk.Label(self.root, text="Controlador de Domo ASCOM Alpaca", font=("Arial", 16))
    self.title_label.pack(pady=20)
        
    # Sección de estado
    self.status_frame = tk.Frame(self.root)
    self.status_frame.pack(pady=10)

    self.status_label = tk.Label(self.status_frame, text="Estado del Domo", font=("Arial", 14))
    self.status_label.grid(row=1, column=0, sticky="w")
    self.status_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_all)
    self.status_button.grid(row=1, column=2)

    # Azimuth
    self.azimuth_label = tk.Label(self.status_frame, text="Azimuth:")
    self.azimuth_label.grid(row=2, column=0, sticky="w")
    self.azimuth_value = tk.Label(self.status_frame, text="...")
    self.azimuth_value.grid(row=2, column=1, sticky="w")
    self.azimuth_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_azimuth)
    self.azimuth_button.grid(row=2, column=2)

    # Home
    self.home_label = tk.Label(self.status_frame, text="En Home:")
    self.home_label.grid(row=3, column=0, sticky="w")
    self.home_value = tk.Label(self.status_frame, text="...")
    self.home_value.grid(row=3, column=1, sticky="w")
    self.home_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_home)
    self.home_button.grid(row=3, column=2)

    # Park
    self.park_label = tk.Label(self.status_frame, text="En Park:")
    self.park_label.grid(row=4, column=0, sticky="w")
    self.park_value = tk.Label(self.status_frame, text="...")
    self.park_value.grid(row=4, column=1, sticky="w")
    self.park_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_park)
    self.park_button.grid(row=4, column=2)

    # Cortina
    self.curtain_label = tk.Label(self.status_frame, text="Cortina:")
    self.curtain_label.grid(row=5, column=0, sticky="w")
    self.curtain_value = tk.Label(self.status_frame, text="...")
    self.curtain_value.grid(row=5, column=1, sticky="w")
    self.curtain_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_curtain)
    self.curtain_button.grid(row=5, column=2)

    # Gajo
    self.gajo_label = tk.Label(self.status_frame, text="Gajo:")
    self.gajo_label.grid(row=6, column=0, sticky="w")
    self.gajo_value = tk.Label(self.status_frame, text="...")
    self.gajo_value.grid(row=6, column=1, sticky="w")
    self.gajo_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_gajo)
    self.gajo_button.grid(row=6, column=2)

    # Slaved
    self.slaved_label = tk.Label(self.status_frame, text="Slaved:")
    self.slaved_label.grid(row=7, column=0, sticky="w")
    self.slaved_label = tk.Label(self.status_frame, text="...")
    self.slaved_label.grid(row=7, column=1)
    self.slaved_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_slaved)
    self.slaved_button.grid(row=7, column=2)

    # En Movimiento
    self.moving_label = tk.Label(self.status_frame, text="En Movimiento:")
    self.moving_label.grid(row=8, column=0, sticky="w")
    self.moving_value = tk.Label(self.status_frame, text="...")
    self.moving_value.grid(row=8, column=1, sticky="w")
    self.moving_button = tk.Button(self.status_frame, text="Actualizar", command=self.update_moving)
    self.moving_button.grid(row=8, column=2)

    # Sección de acciones
    self.actions_frame = tk.Frame(self.root)
    self.actions_frame.pack(pady=20)

    self.close_curtain_button = tk.Button(self.actions_frame, text="Cerrar Cortina", command=self.close_curtain)
    self.close_curtain_button.grid(row=0, column=0, pady=5)

    self.go_home_button = tk.Button(self.actions_frame, text="Ir a Home", command=self.go_home)
    self.go_home_button.grid(row=1, column=0, pady=5)

    self.open_curtain_button = tk.Button(self.actions_frame, text="Abrir Cortina", command=self.open_curtain)
    self.open_curtain_button.grid(row=2, column=0, pady=5)

    self.open_curtain_no_gajo_button = tk.Button(self.actions_frame, text="Abrir Cortina sin Gajo", command=self.open_curtain_no_gajo)
    self.open_curtain_no_gajo_button.grid(row=3, column=0, pady=5)

    self.park_button = tk.Button(self.actions_frame, text="Park", command=self.park)
    self.park_button.grid(row=4, column=0, pady=5)

    self.indicate_park_button = tk.Button(self.actions_frame, text="Indicar Park", command=self.indicate_park)
    self.indicate_park_button.grid(row=5, column=0, pady=5)

    self.move_to_azimuth_label = tk.Label(self.actions_frame, text="Mover a Azimuth:")
    self.move_to_azimuth_label.grid(row=6, column=0, pady=5)
    self.azimuth_entry = tk.Entry(self.actions_frame)
    self.azimuth_entry.grid(row=7, column=0, pady=5)
    self.move_to_azimuth_button = tk.Button(self.actions_frame, text="Mover", command=self.move_to_azimuth)
    self.move_to_azimuth_button.grid(row=8, column=0, pady=5)

    self.close_curtain_button = tk.Button(self.actions_frame, text="Detener movimiento", command=self.abort_slew)
    self.close_curtain_button.grid(row=9, column=0, pady=5)

  def update_all(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/devicestate', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      values = response_json['Value']
      for valueObj in values:
        if valueObj['Name'] == 'Azimuth':
          self.azimuth_value.config(text=valueObj['Value'])
        elif valueObj['Name'] == 'AtHome':
          value = valueObj['Value']
          if value:
            self.home_value.config(text="Sí")
          else:
            self.home_value.config(text="No")
        elif valueObj['Name'] == 'AtPark':
          value = valueObj['Value']
          if value:
            self.park_value.config(text="Sí")
          else:
            self.park_value.config(text="No")
        elif valueObj['Name'] == 'ShutterStatus':
          shutter_state = valueObj['Value']
          if shutter_state == 0:
            self.curtain_value.config(text="Abierta")
          elif shutter_state == 1:
            self.curtain_value.config(text="Derrada")
          elif shutter_state == 2:
            self.curtain_value.config(text="Abriendo")
          elif shutter_state == 3:
            self.curtain_value.config(text="Cerrando")
          elif shutter_state == 4:
            self.curtain_value.config(text="Error")
        elif valueObj['Name'] == 'Slewing':
          value = valueObj['Value']
          if value:
            self.moving_value.config(text="Sí")
          else:
            self.moving_value.config(text="No")

  def update_azimuth(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/azimuth', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      self.azimuth_value.config(text=response_json['Value'])

  def update_home(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/athome', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      value = response_json['Value']
      if value:
        self.home_value.config(text="Sí")
      else:
        self.home_value.config(text="No")

  def update_park(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/atpark', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      value = response_json['Value']
      if value:
        self.park_value.config(text="Sí")
      else:
        self.park_value.config(text="No")

  def update_curtain(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/shutterstatus', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      value = response_json['Value']
      if value == 0:
        self.curtain_value.config(text="Abierta")
      elif value == 1:
        self.curtain_value.config(text="Cerrada")
      elif value == 2:
        self.curtain_value.config(text="Abriendo")
      elif value == 3:
        self.curtain_value.config(text="Cerrando")
      elif value == 4:
        self.curtain_value.config(text="Error")

  def update_gajo(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/commandstring', data={
      'ClientTransactionID': self.transaction_id,
      'Command': 'flapStatus',
      'Raw': True
      }
    )
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      value = response_json['Value']
      if value == '0':
        self.gajo_value.config(text="Abajo")
      elif value == '1':
        self.gajo_value.config(text="Abriendo")
      elif value == '2':
        self.gajo_value.config(text="Arriba")
      elif value == '3': 
        self.gajo_value.config(text="Cerrando")

  def update_slaved(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/slaved', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      value = response_json['Value']
      if value:
        self.slaved_label.config(text="Sí")
      else:
        self.slaved_label.config(text="No")

  def update_moving(self):
    response = requests.get(self.server_address + '/api/v1/dome/0/slewing', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      value = response_json['Value']
      if value:
        self.moving_value.config(text="Sí")
      else:
        self.moving_value.config(text="No")

  def close_curtain(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/closeshutter', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al cerrar la cortina: {response_json['ErrorMessage']}")
        return
      else:
        self.curtain_value.config(text="Cerrando")
        messagebox.showinfo("Cerrar cortina", "Cerrando cortina")
    else:
      messagebox.showerror("Error", f"Error al cerrar la cortina: {response.text}")

  def go_home(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/findhome', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al ir a home: {response_json['ErrorMessage']}")
        return
      else:
        messagebox.showinfo("Ir a home", f"Domo moviendose a home")
    else:
      messagebox.showerror("Error", f"Error al ir a home: {response.text}")

  def open_curtain(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/openshutter', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al abrir cortina: {response_json['ErrorMessage']}")
        return
      else:
        self.curtain_value.config(text="Abriendo")
        messagebox.showinfo("Ir a home", "Abriendo cortina")
    else:
      messagebox.showerror("Error", f"Error al abrir cortina: {response.text}")

  def open_curtain_no_gajo(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/action', data={
      'ClientTransactionID': self.transaction_id,
      'Action': 'openWithoutFlap',
      'Parameters': ''
    })
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al abrir cortina sin gajo: {response_json['ErrorMessage']}")
        return
      else:
        self.curtain_value.config(text="Abriendo")
        self.gajo_value.config(text="Abriendo")
        messagebox.showinfo("Abrir cortina sin gajo", f"Abriendo sin gajo")
    else:
      messagebox.showerror("Error", f"Error al abrir cortina sin gajo: {response.text}")

  def park(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/park', data={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al ir a park: {response_json['ErrorMessage']}")
        return
      else:
        messagebox.showinfo("Ir a park", "Domo moviendose a park")
    else:
      messagebox.showerror("Error", f"Error al ir a park: {response.text}")


  def indicate_park(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/setpark', data={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al indicar park: {response_json['ErrorMessage']}")
        return
      else:
        messagebox.showinfo("Indicar park", "Posicion de park actualizada")
    else:
      messagebox.showerror("Error", f"Error al actualizar posicion de park: {response.text}")

  def move_to_azimuth(self):
    azimuth = self.azimuth_entry.get()
    try:
      azimuth = float(azimuth)
    except ValueError:
      messagebox.showerror("Error", "Azimuth debe ser un numero")
      self.azimuth_entry.delete(0, tk.END)
      return
    
    if azimuth < 0 or azimuth > 360:
      messagebox.showerror("Error", "Azimuth fuera de rango (0-360)")
      return

    response = requests.put(self.server_address + '/api/v1/dome/0/slewtoazimuth', data={
      'ClientTransactionID': self.transaction_id,
      'Azimuth': azimuth
      })
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al mover a azimuth: {error}")
        return
      else:
        messagebox.showinfo("Mover a azimuth", "Moviendo domo a azimuth")
    else:
      messagebox.showerror("Error", f"Error al mover a azimuth: {response.text}")

  def abort_slew(self):
    response = requests.put(self.server_address + '/api/v1/dome/0/abortslew', params={'ClientTransactionID': self.transaction_id})
    self.transaction_id += 1
    if response.status_code == 200:
      response_json = response.json()
      error = response_json['ErrorNumber']
      if error > 0:
        messagebox.showerror("Error", f"Error al detener movimiento: {response_json['ErrorMessage']}")
        return
      else:
        messagebox.showinfo("Detener movimiento", "Movimiento detenido")
    else:
      messagebox.showerror("Error", f"Error al detener movimiento: {response.text}")