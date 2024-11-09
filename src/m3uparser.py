import re
import requests

class M3UParser:
    def __init__(self, file_path=None):
        self.channels = {
            'Streams': {},
            'Films and Series': {}
        }
        if file_path:
            self.load_from_file_path(file_path)

    def load_from_file_path(self, file_path):
        """
        Carga y analiza la lista M3U desde una URL, almacenando los canales en `self.channels`.
        """
        with open(file_path, encoding="utf8") as f:
            response = f.read()
        lines = response.splitlines()
        self._parse(lines)

    def _parse(self, lines):
        """
        Parsea las líneas de la lista M3U y extrae la información de los canales.
        """
        channel_info = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("#EXTINF:"):
                # Extraemos la información después de #EXTINF:
                channel_info = self._parse_extinf(line)
            
            elif line and not line.startswith("#"):
                # Esta línea es la URL del canal
                channel_info["url"] = line
                
                # Agregar canal a estructuras
                flag = 'Streams' if str(line).endswith('.ts') else 'Films and Series'
                if channel_info['title'] not in self.channels[flag]:
                    self.channels[flag][channel_info['title']] = {}
                self.channels[flag][channel_info['title']][channel_info['name']] = channel_info
                
                channel_info = {}  # Reiniciar para el próximo canal

    def _parse_extinf(self, line):
        """
        Parsea una línea de información EXTINF y devuelve un diccionario con los datos del canal.
        """
        channel_info = {}
        
        # Expresión regular para capturar atributos del tipo key="value"
        attributes = re.findall(r'(\w+?)="(.*?)"', line)
        for key, value in attributes:
            channel_info[key] = value
        
        # Buscar el nombre del canal después de la coma
        name_match = re.search(r',(.+)', line)
        if name_match:
            channel_info["name"] = name_match.group(1).strip()
        
        return channel_info

    def get_channels(self):
        """
        Devuelve la lista de canales analizados.
        """
        return self.channels

"""
file_path = "C:/Users/David/Downloads/playlist_zFudDfgmuS_plus.m3u"
parser = M3UParser(file_path)
channels = parser.get_channels()

for channel in channels:
    print(channel)
print(channels)
"""