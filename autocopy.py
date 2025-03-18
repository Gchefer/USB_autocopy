import os
import shutil
import time
import win32file
import win32api

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

def copy_files_to_usb(usb_path, source_folder):
    """Copia arquivos da pasta de origem para o pen drive"""
    try:
        for item in os.listdir(source_folder):
            source_path = os.path.join(source_folder, item)
            dest_path = os.path.join(usb_path, item)
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
                print(f"Arquivo copiado: {item}")
        print(f"Cópia concluída para: {usb_path}")
        
        # Ejetar o USB após a cópia
        eject_usb(usb_path)
    except Exception as e:
        print(f"Erro ao copiar arquivos: {e}")

def eject_usb(drive):
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

        print(f"Pen drive {drive} ejetado com sucesso.")
    except Exception as e:
        print(f"Erro ao ejetar {drive}: {e}")

def monitor_usb(source_folder):
    """Monitora a conexão de novos dispositivos USB"""
    print("Monitorando dispositivos USB...")
    known_drives = set(get_usb_drives())
    while True:
        current_drives = set(get_usb_drives())
        new_drives = current_drives - known_drives
        if new_drives:
            for drive in new_drives:
                print(f"Pen drive detectado: {drive}")
                copy_files_to_usb(drive, source_folder)
        known_drives = current_drives
        time.sleep(2)

if __name__ == "__main__":
    SOURCE_FOLDER = "D:\\musica_autocopy"  # Altere para a pasta de origem dos arquivos
    monitor_usb(SOURCE_FOLDER)
