import os
import shutil
import time
import win32file
import win32api
import threading

def get_usb_drives():
    """Retorna uma lista de unidades USB conectadas"""
    drives = []
    bitmask = win32file.GetLogicalDrives()
    for i in range(26):
        if bitmask & (1 << i):
            drive = f"{chr(65 + i)}:\\"
            if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                drives.append(drive)
    return drives

def copy_files_to_usb(usb_path, source_folder, log_callback, progress_callback):
    """Copia arquivos da pasta de origem para o pen drive"""
    if not source_folder:
        log_callback("Erro: Nenhuma pasta selecionada!")
        return

    usb_dest_folder = os.path.join(usb_path, os.path.basename(source_folder))
    
    if os.path.exists(usb_dest_folder):
        log_callback(f"Pasta já existente em {usb_path}, pulando cópia.")
        return

    try:
        os.makedirs(usb_dest_folder, exist_ok=True)
        files = os.listdir(source_folder)
        total_size = sum(os.path.getsize(os.path.join(source_folder, f)) for f in files if os.path.isfile(os.path.join(source_folder, f)))

        copied_size = 0
        for item in files:
            source_path = os.path.join(source_folder, item)
            dest_path = os.path.join(usb_dest_folder, item)
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
                copied_size += os.path.getsize(source_path)
                progress_percent = int((copied_size / total_size) * 100)
                progress_callback(progress_percent)
                log_callback(f"Copiado: {item} ({copied_size // (1024*1024)} MB de {total_size // (1024*1024)} MB)")

        log_callback(f"Cópia concluída para: {usb_path}")
        eject_usb(usb_path, log_callback)
    except Exception as e:
        log_callback(f"Erro ao copiar arquivos: {e}")

def eject_usb(drive, log_callback):
    """Ejeta o dispositivo USB"""
    try:
        volume_name = f"\\\\.\\{drive[:-1]}"
        handle = win32file.CreateFile(
            volume_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        win32file.DeviceIoControl(handle, 0x2D4808, None, None)
        win32file.CloseHandle(handle)
        log_callback(f"Pen drive {drive} ejetado com sucesso.")
    except Exception as e:
        log_callback(f"Erro ao ejetar {drive}: {e}")

def monitor_usb(source_folder, log_callback, progress_callback, stop_event):
    """Monitora dispositivos USB e inicia a cópia quando um novo dispositivo é detectado"""
    log_callback("Monitorando dispositivos USB...")
    known_drives = set(get_usb_drives())
    while not stop_event.is_set():
        current_drives = set(get_usb_drives())
        new_drives = current_drives - known_drives
        if new_drives:
            for drive in new_drives:
                log_callback(f"Pen drive detectado: {drive}")
                copy_files_to_usb(drive, source_folder, log_callback, progress_callback)
        known_drives = current_drives
        time.sleep(2)

def start_monitoring(source_folder, log_callback, progress_callback, stop_event):
    """Inicia a thread de monitoramento USB"""
    stop_event.clear()
    monitor_thread = threading.Thread(target=monitor_usb, args=(source_folder, log_callback, progress_callback, stop_event))
    monitor_thread.start()
    return monitor_thread

def stop_monitoring(stop_event, log_callback):
    """Para o monitoramento de USB"""
    stop_event.set()
    log_callback("Monitoramento interrompido.")
