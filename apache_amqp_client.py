# Apache ActiveMQ Classic + Artemis 2.x AMQP Sender Tool 1.0

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
import threading
import time
import base64
import os
from datetime import datetime
import uuid
import re

class ArtemisClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Apache ActiveMQ Classic + Artemis 2.x AMQP Sender Tool 1.0")
        self.geometry("600x600")
        self.minsize(600, 600)

        self.container = None
        self.client = None
        self.connection_lock = threading.Lock()
        self.attached_file = None

        self.create_widgets()
        self.configure_grid()

    def configure_grid(self):
        self.grid_columnconfigure(1, weight=1)
        for i in range(8):
            self.grid_rowconfigure(i, weight=0)
        self.grid_rowconfigure(6, weight=1)

    def create_widgets(self):
        # Server address (Host:Port)
        ttk.Label(self, text="Server:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.server_entry = ttk.Entry(self)
        self.server_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.server_entry.insert(0, "127.0.0.1:61716")

        # Username
        ttk.Label(self, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.user_entry = ttk.Entry(self)
        self.user_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Password
        ttk.Label(self, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.pass_entry = ttk.Entry(self, show="*")
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Queue
        ttk.Label(self, text="Queue:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.queue_entry = ttk.Entry(self)
        self.queue_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.queue_entry.insert(0, "test_queue")

        # Message field
        self.msg_frame = ttk.Frame(self)
        self.msg_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        ttk.Label(self.msg_frame, text="Message:").pack(anchor='w')
        self.msg_entry = scrolledtext.ScrolledText(self.msg_frame, height=4)
        self.msg_entry.pack(fill='both', expand=True)

        # File attachment
        self.file_frame = ttk.Frame(self)
        self.file_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.attach_btn = ttk.Button(self.file_frame, text="Attach File", command=self.attach_file)
        self.attach_btn.pack(side='left', padx=5)
        self.detach_btn = ttk.Button(self.file_frame, text="✕", command=self.detach_file, state=tk.DISABLED, width=2)
        self.detach_btn.pack(side='left', padx=5)
        self.file_label = ttk.Label(self.file_frame, text="No file selected")
        self.file_label.pack(side='left', fill='x', expand=True)

        # Logs
        logs_frame = ttk.Frame(self)
        logs_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        ttk.Label(logs_frame, text="Logs:").pack(anchor='w')
        self.log_area = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD)
        self.log_area.pack(fill='both', expand=True)

        # Send button
        self.send_btn = ttk.Button(self, text="Send Message", command=self.send_message)
        self.send_btn.grid(row=7, column=0, columnspan=2, pady=10, sticky='ew')

    def attach_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.attached_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.detach_btn.config(state=tk.NORMAL)

            self.msg_entry.config(state=tk.NORMAL)
            self.msg_entry.delete("1.0", tk.END)
            self.msg_entry.insert(tk.END, "Message field disabled when file is attached")
            self.msg_entry.config(state=tk.DISABLED, bg='#f0f0f0', foreground='#666666')

    def detach_file(self):
        self.attached_file = None
        self.file_label.config(text="No file selected")
        self.detach_btn.config(state=tk.DISABLED)

        self.msg_entry.config(state=tk.NORMAL, bg='white', foreground='black')
        self.msg_entry.delete("1.0", tk.END)

    def parse_host_port(self, server_str):
        pattern = r"^([a-zA-Z0-9.-]+):(\d{1,5})$"
        match = re.match(pattern, server_str)
        if match:
            host, port = match.groups()
            if 0 < int(port) <= 65535:
                return host, int(port)
        return None, None

    def send_message(self):
        try:
            server_str = self.server_entry.get().strip()
            host, port = self.parse_host_port(server_str)
            if not host or not port:
                messagebox.showerror("Invalid server address", "Enter address in 'host:port' format, e.g., 127.0.0.1:61716")
                return

            message = self.msg_entry.get("1.0", tk.END).strip()
            file_data = None

            if self.attached_file:
                with open(self.attached_file, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')

            if not message and not file_data:
                self.log("Error: Cannot send empty message")
                return

            if not self.client or not self.client.is_connected():
                self.connect_artemis(host, port)
                for _ in range(10):
                    if self.client and self.client.is_ready():
                        break
                    time.sleep(0.1)
                else:
                    raise ConnectionError("Failed to establish connection")

            message_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            payload = {
                'text': message,
                'file_name': os.path.basename(self.attached_file) if self.attached_file else None,
                'file_data': file_data,
                'message_id': message_id,
                'timestamp': timestamp
            }

            self.client.send(payload)
            queue_name = self.queue_entry.get()
            self.log(f"Message sent to {queue_name}\nID: {message_id}\nTimestamp: {timestamp}")

            if self.attached_file:
                self.detach_file()

        except Exception as e:
            self.log(f"Error: {str(e)}")

    def connect_artemis(self, host, port):
        with self.connection_lock:
            if self.client and self.client.is_connected():
                return

            try:
                url = f"amqp://{host}:{port}"
                self.client = ArtemisSender(
                    url=url,
                    address=self.queue_entry.get(),
                    username=self.user_entry.get(),
                    password=self.pass_entry.get()
                )

                self.container = Container(self.client)
                threading.Thread(target=self.container.run, daemon=True).start()
                self.log("Connecting to message broker...")

            except Exception as e:
                self.log(f"Connection error: {str(e)}")
                self.client = None

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

class ArtemisSender(MessagingHandler):
    def __init__(self, url, address, username, password):
        super().__init__()
        self.url = url
        self.address = address
        self.username = username
        self.password = password
        self.sender = None
        self.connection = None
        self.connected = False
        self.ready = threading.Event()

    def on_start(self, event):
        self.connection = event.container.connect(
            self.url,
            user=self.username,
            password=self.password,
            allow_insecure_mechs=True
        )
        self.sender = event.container.create_sender(self.connection, self.address)
        
    def on_link_opened(self, event):
        if event.sender == self.sender:
            self.connected = True
            self.ready.set()

    def send(self, payload):
        if not self.ready.is_set():
            raise ConnectionError("Connection not ready")
        
        msg = Message()
        
        if payload['file_data']:
            msg.body = payload['file_data']
            msg.properties = {
                'file_name': payload['file_name'],
                'is_file': True,
                'message_id': payload['message_id'],
                'timestamp': payload['timestamp']
            }
        else:
            msg.body = payload['text']
            msg.properties = {
                'is_file': False,
                'message_id': payload['message_id'],
                'timestamp': payload['timestamp']
            }
        
        self.sender.send(msg)

    def is_connected(self):
        return self.connected
        
    def is_ready(self):
        return self.ready.is_set()

    def on_disconnected(self, event):
        self.connected = False
        self.ready.clear()

if __name__ == "__main__":
    app = ArtemisClientGUI()
    app.mainloop()
