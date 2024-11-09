# M3UPlyer
This app is intended to reproduce M3U playlists using VLC. Do you need to define the file %LOCALAPPDATA%/M3UPlayer/conf.json to make the application work:
```json
{
    "url": "your url m3u",
    "vlc_path": "your path to vlc"
}
```

To run the app:
```bash
python src/main.py
```

To create an .exe, you can use pyinstaller:
```bash
pyinstaller --noconsole --add-data ".\img\icon.ico:."  -p .\venv\Lib\site-packages\ --onefile src/main.py
```