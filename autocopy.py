import os
import shutil
import time
import win32file
import win32api
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def get_usb_drives():
    """Retorna uma lista de unidades USB conectadas"""
    drives = []
    bitmask = win32file.GetLogicalDrives()
    for i in range(26):  # Verifica todas as letras de A: a Z:
        if bitmask & (1 << i):
            drive = f"{chr(65 + i)}:\\"
            if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                drives.append(drive)
    return drives

def copy_files_to_usb(usb_path, source_folder, log_widget):
    """Copia arquivos da pasta de origem para o pen drive"""
    try:
        for item in os.listdir(source_folder):
            source_path = os.path.join(source_folder, item)
            dest_path = os.path.join(usb_path, item)
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
                log_widget.insert(tk.END, f"Arquivo copiado: {item}\n")
        log_widget.insert(tk.END, f"Cópia concluída para: {usb_path}\n")
        
        # Ejetar o USB após a cópia
        eject_usb(usb_path, log_widget)
    except Exception as e:
        log_widget.insert(tk.END, f"Erro ao copiar arquivos: {e}\n")

def eject_usb(drive, log_widget):
    """Ejeta o dispositivo USB"""
    try:
        volume_name = f"\\\\.\\{drive[:-1]}"  # Remove a barra invertida do final
        handle = win32file.CreateFile(
            volume_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        
        # Código correto para ejeção
        win32file.DeviceIoControl(handle, 0x2D4808, None, None)
        win32file.CloseHandle(handle)

        log_widget.insert(tk.END, f"Pen drive {drive} ejetado com sucesso.\n")
    except Exception as e:
        log_widget.insert(tk.END, f"Erro ao ejetar {drive}: {e}\n")

def monitor_usb(source_folder, log_widget):
    """Monitora a conexão de novos dispositivos USB"""
    log_widget.insert(tk.END, "Monitorando dispositivos USB...\n")
    known_drives = set(get_usb_drives())
    while True:
        current_drives = set(get_usb_drives())
        new_drives = current_drives - known_drives
        if new_drives:
            for drive in new_drives:
                log_widget.insert(tk.END, f"Pen drive detectado: {drive}\n")
                copy_files_to_usb(drive, source_folder, log_widget)
        known_drives = current_drives
        time.sleep(2)

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        source_folder.set(folder_selected)
        log_widget.insert(tk.END, f"Pasta selecionada: {folder_selected}\n")

def start_monitoring():
    folder = source_folder.get()
    if not folder:
        messagebox.showwarning("Aviso", "Selecione uma pasta antes de iniciar o monitoramento.")
        return
    monitor_usb(folder, log_widget)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Copiar Arquivos para USB")

# Variável para armazenar a pasta de origem
source_folder = tk.StringVar()

# Frame para seleção de pasta
frame = tk.Frame(root)
frame.pack(pady=10)

label = tk.Label(frame, text="Pasta de Origem:")
label.pack(side=tk.LEFT)

entry = tk.Entry(frame, textvariable=source_folder, width=50)
entry.pack(side=tk.LEFT, padx=5)

button_select = tk.Button(frame, text="Selecionar Pasta", command=select_folder)
button_select.pack(side=tk.LEFT)

# Botão para iniciar o monitoramento
button_start = tk.Button(root, text="Iniciar Monitoramento", command=start_monitoring)
button_start.pack(pady=10)

# Área de log
log_widget = scrolledtext.ScrolledText(root, width=80, height=20)
log_widget.pack(padx=10, pady=10)

# Iniciar a interface gráfica
root.mainloop()