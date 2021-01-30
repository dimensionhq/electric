from colorama import Fore
import requests
import sys
import cursor
import os
import win32com
import win32com.client
import zipfile
import tarfile
import py7zr
import patoolib
from tqdm import tqdm

home = os.path.expanduser('~')

def delete_start_menu_shortcut(shortcut_name):
    start_menu = os.environ['APPDATA'] + R'\Microsoft\Windows\Start Menu\Programs\Electric'
    path = os.path.join(start_menu, f'{shortcut_name}.lnk')
    os.remove(path)

def unzip_file(download_dir: str, unzip_dir_name: str, file_type: str):
    if not unzip_dir_name:
        unzip_dir_name = download_dir.replace('.zip', '')
    if not os.path.isdir(rf'{home}\electric'):
        os.mkdir(rf'{home}\electric')
    os.chdir(rf'{home}\electric')
    if file_type == '.zip':
        with zipfile.ZipFile(download_dir, 'r') as zf:
            for member in tqdm(zf.infolist(), desc='Extracting Files', bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}', unit='files'):
                try:
                    zf.extract(member, download_dir.replace('.zip', ''))
                except zipfile.error:
                 pass
    if file_type == '.tar':
        tar = tarfile.open(download_dir)
        tar.extractall(unzip_dir_name)
        tar.close()
    if file_type == '.7z':
        with py7zr.SevenZipFile(download_dir) as z:
            z.extractall(unzip_dir_name)
    if file_type == '.rar':
        patoolib.extract_archive(download_dir, outdir=unzip_dir_name)
  
    os.remove(download_dir)
    return rf'{home}\electric\\' + unzip_dir_name.replace(file_type, '')

def install_font(src_path: str):
        from ctypes import wintypes
        import ctypes
        import os
        import shutil
        import winreg

        user32 = ctypes.WinDLL('user32', use_last_error=True)
        gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

        FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'

        HWND_BROADCAST = 0xFFFF
        SMTO_ABORTIFHUNG = 0x0002
        WM_FONTCHANGE = 0x001D
        GFRI_DESCRIPTION = 1
        GFRI_ISTRUETYPE = 3

        if not hasattr(wintypes, 'LPDWORD'):
            wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

        user32.SendMessageTimeoutW.restype = wintypes.LPVOID
        user32.SendMessageTimeoutW.argtypes = (
            wintypes.HWND,   # hWnd
            wintypes.UINT,   # Msg
            wintypes.LPVOID, # wParam
            wintypes.LPVOID, # lParam
            wintypes.UINT,   # fuFlags
            wintypes.UINT,   # uTimeout
            wintypes.LPVOID  # lpdwResult
        )

        gdi32.AddFontResourceW.argtypes = (
            wintypes.LPCWSTR,) # lpszFilename

        # http://www.undocprint.org/winspool/getfontresourceinfo
        gdi32.GetFontResourceInfoW.argtypes = (
            wintypes.LPCWSTR, # lpszFilename
            wintypes.LPDWORD, # cbBuffer
            wintypes.LPVOID,  # lpBuffer
            wintypes.DWORD)   # dwQueryType

        # copy the font to the Windows Fonts folder
        dst_path = os.path.join(
            os.environ['SystemRoot'], 'Fonts', os.path.basename(src_path)
        )
        shutil.copy(src_path, dst_path)

        # load the font in the current session
        if not gdi32.AddFontResourceW(dst_path):
            os.remove(dst_path)
            raise WindowsError('AddFontResource failed to load "%s"' % src_path)

        # notify running programs
        user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None
        )

        # store the fontname/filename in the registry
        filename = os.path.basename(dst_path)
        fontname = os.path.splitext(filename)[0]

        # try to get the font's real name
        cb = wintypes.DWORD()
        if gdi32.GetFontResourceInfoW(
                filename, ctypes.byref(cb), None, GFRI_DESCRIPTION
        ):
            buf = (ctypes.c_wchar * cb.value)()
            if gdi32.GetFontResourceInfoW(
                    filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION
            ):
                fontname = buf.value

        is_truetype = wintypes.BOOL()
        cb.value = ctypes.sizeof(is_truetype)
        gdi32.GetFontResourceInfoW(
            filename, ctypes.byref(cb), ctypes.byref(is_truetype), GFRI_ISTRUETYPE
        )

        if is_truetype:
            fontname += ' (TrueType)'

        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)

def download(url: str, download_extension: str, file_path: str, show_progress_bar=True):
    '''
    Downloads A File from a URL And Saves It To A location
    url `(str)`:  Link or URL to download the file from.
    download_extension`(string)`: Extension for the file downloaded like `.exe` or `.txt`. 
    
    file_path`(string)`: Path to save the file to. 
    Examples(`'C:\\Users\\name\\Downloads'`, `'~/Desktop'`)
    show_progress_bar `[Optional]` `(bool)`: Whether or not to show the progress bar while downloading.
    >>> download('https://atom.io/download/windows_x64', '.exe', 'C:\MyDir\Installer')
    '''
    cursor.hide() # Use This If You Want to Hide The Cursor While Downloading The File In The Terminal
    if not os.path.isdir(rf'{home}\electric'):
        os.mkdir(rf'{home}\electric')
    try:
        with open(f'{file_path}{download_extension}', 'wb') as f:
            # Get Response From URL
            response = requests.get(url, stream=True)
            # Find Total Download Size
            total_length = response.headers.get('content-length')
            # Number Of Iterations To Write To The File
            chunk_size = 4096
            
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                full_length = int(total_length)
                
                # Write Data To File
                for data in response.iter_content(chunk_size=chunk_size):
                    dl += len(data)
                    f.write(data)

                    if show_progress_bar:
                        complete = int(25 * dl / full_length)
                        fill_c =  Fore.GREEN + '=' * complete # Replace '=' with the character you want like '#' or '$'
                        unfill_c = Fore.LIGHTBLACK_EX + '-' * (25 - complete) # Replace '-' with the character you want like ' ' (whitespace)
                        sys.stdout.write(
                            f'\r{fill_c}{unfill_c} {Fore.RESET} {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB {Fore.RESET}')
                        sys.stdout.flush()
        print(f'\n{Fore.GREEN}Initializing Unzipper{Fore.RESET}')
    except KeyboardInterrupt:
        print(f'\n{Fore.RED}Download Was Interrupted!{Fore.RESET}')
        sys.exit()

def create_start_menu_shortcut(unzip_dir, file_name, shortcut_name):
    start_menu = os.environ['APPDATA'] + R'\Microsoft\Windows\Start Menu\Programs\Electric'
    if not os.path.isdir(start_menu):
        os.mkdir(start_menu)
    
    path = os.path.join(start_menu, f'{shortcut_name}.lnk')
    os.chdir(unzip_dir)
    icon = unzip_dir + '\\' + file_name
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = unzip_dir + '\\' + file_name
    shortcut.IconLocation = icon
    shortcut.WindowStyle = 7 # 7 - Minimized, 3 - Maximized, 1 - Normal
    shortcut.save()

def generate_shim(shim_command: str, shim_name: str, shim_extension: str):
    shim_command += f'\\{shim_name}'
    shim_command = shim_command.replace('\\\\', '\\')
    if not os.path.isdir(rf'{home}\electric\shims'):
        os.mkdir(rf'{home}\electric\shims')
    
    with open(rf'{home}\electric\shims\{shim_name}.bat', 'w+') as f:
        f.write(f'@echo off\n"{shim_command}.{shim_extension}"')

# Scoop logs
# Installing 'atom' (1.54.0) [64bit]
# atom-x64-1.54.0-full.nupkg (182.7 MB) [==========================================================================================================================] 100%
# Checking hash of atom-x64-1.54.0-full.nupkg ... ok.
# Extracting atom-x64-1.54.0-full.nupkg ... done.
# Linking ~\scoop\apps\atom\current => ~\scoop\apps\atom\1.54.0
# Creating shim for 'atom'.
# Creating shim for 'apm'.
# Creating shortcut for Atom (atom.exe)
# 'atom' (1.54.0) was installed successfully!