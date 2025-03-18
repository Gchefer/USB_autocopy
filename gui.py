import tkinter as tk
from tkinter import ttk, filedialog 
from threading import Thread
import usb_copy

class UsbCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB AutoCopy")
        self.root.geometry("500x400")

        self.source_folder = ""
        
        self.label = tk.Label(root, text="Selecione a pasta para copiar:")
        self.label.pack(pady=5)
        
        self.select_btn = tk.Button(root, text="Selecionar Pasta", command=self.select_folder)
        self.select_btn.pack(pady=5)

        self.start_btn = tk.Button(root, text="Iniciar Monitoramento", command=self.start_monitoring)
        self.start_btn.pack(pady=5)
        
        self.progress = tk.IntVar()
        self.progress_bar = tk.ttk.Progressbar(root, length=400, mode="determinate", variable=self.progress)
        self.progress_bar.pack(pady=10)
        
        self.log_text = tk.Text(root, height=10, width=60)
        self.log_text.pack(pady=10)

    def select_folder(self):
        self.source_folder = filedialog.askdirectory()
        self.log(f"Pasta selecionada: {self.source_folder}")

    def start_monitoring(self):
        if not self.source_folder:
            self.log("Selecione uma pasta primeiro!")
            return
        
        self.log("Iniciando monitoramento de USB...")
        thread = Thread(target=usb_copy.monitor_usb, args=(self.source_folder, self.log, self.update_progress), daemon=True)
        thread.start()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def update_progress(self, value):
        self.progress.set(value)

if __name__ == "__main__":
    root = tk.Tk()
    app = UsbCopyApp(root)
    root.mainloop()
