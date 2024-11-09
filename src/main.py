import os
import sys
import json
from m3uplayer import M3UPlayerApp
import tkinter as tk

PATH_TO_CONF = os.path.join(os.getenv("LOCALAPPDATA"), 'M3UPlayer', 'conf.json')
PATH_TO_LIST = os.path.join(os.getenv("LOCALAPPDATA"), 'M3UPlayer', 'list.m3u')

if __name__ == '__main__':
    try:
        with open(PATH_TO_CONF) as f:
            conf = json.load(f)
    except:
        print(f'Configuration file {PATH_TO_CONF} does not exists', file=sys.stderr)
        sys.exit(1)
    if 'url' not in conf:
        print(f'Configuration file {PATH_TO_CONF} does not have the key "url" defined', file=sys.stderr)
        sys.exit(1)
    if 'vlc_path' not in conf:
        print(f'Configuration file {PATH_TO_CONF} does not have the key "vlc_path" defined', file=sys.stderr)
        sys.exit(1)

    # Iniciar la interfaz gráfica
    root = tk.Tk()
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'icon.ico')
    app = M3UPlayerApp(root, PATH_TO_LIST, conf)
    root.iconbitmap(icon_path)
    root.mainloop()