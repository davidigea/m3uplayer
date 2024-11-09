import tkinter as tk
from m3uparser import M3UParser
import subprocess
import requests
import os
import time

# La clase principal para la interfaz gráfica
class M3UPlayerApp:
    def __init__(self, root, m3u_path, conf):
        self.root = root
        self.m3u_path = m3u_path
        self.conf = conf
        self.root.title("M3U Player")
        self.root.geometry("400x600")
        self.root.configure(bg="#2e3b4e")
        
        # Crear un player
        self.player = None
        
        # Categoría actual
        self.current_category = None

        # Recuperar M3U vía web en caso de que sea necesario
        # Cuando no existe o cuando lleva 24 horas o más sin actualizarse
        if not os.path.exists(self.m3u_path) or (time.time() - os.path.getmtime(self.m3u_path) >= 86400):
            self.refresh_list_aux()
        
        self.parser = M3UParser(self.m3u_path)
        self.channels = self.parser.get_channels()

        # Frame principal de la interfaz
        self.main_frame = tk.Frame(root, bg="#2e3b4e")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Etiqueta de título
        title_label = tk.Label(self.main_frame, text="IPTV Player", font=("Helvetica", 16, "bold"), bg="#2e3b4e", fg="white")
        title_label.pack(pady=10)
        
        # Botón de refrescar
        ref_frame = tk.Frame(self.main_frame, bg="#2e3b4e")
        ref_frame.pack(pady=10)
        self.films_button = tk.Button(ref_frame, text="Refresh list", command=self.refresh_list, bg="#FFCC99", fg="white", font=("Helvetica", 12, 'bold'), width=15)
        self.films_button.pack(side=tk.BOTTOM, padx=5)

        # Botones de Streams y Films and Series
        btn_frame = tk.Frame(self.main_frame, bg="#2e3b4e")
        btn_frame.pack(pady=10)

        self.streams_button = tk.Button(btn_frame, text="Streams", command=self.show_streams, bg="#4a90e2", fg="white", font=("Helvetica", 12, 'bold'), width=15)
        self.streams_button.pack(side=tk.LEFT, padx=5)

        self.films_button = tk.Button(btn_frame, text="Films and Series", command=self.show_films_and_series, bg="#50e3c2", fg="white", font=("Helvetica", 12, 'bold'), width=15)
        self.films_button.pack(side=tk.RIGHT, padx=5)

        # Etiqueta que muestra la categoría seleccionada
        self.category_label = tk.Label(self.main_frame, text="", font=("Helvetica", 12), bg="#2e3b4e", fg="white")
        self.category_label.pack(pady=5)

        # Campo de búsqueda
        self.search_var = tk.StringVar()
        self.trace_res = self.search_var.trace_add("write", self.filter_channels)

        search_frame = tk.Frame(self.main_frame, bg="#2e3b4e", width=30)
        search_frame.pack(pady=10)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 12), width=30, exportselection=0)
        self.search_entry.pack(pady=5)
        self.search_entry.insert(0, "Search...")  # Texto inicial en el cuadro de búsqueda

        # Bind de eventos para manejar la entrada
        self.search_entry.bind("<FocusIn>", self.on_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_focus_out)

        # Frame para la lista y la barra de desplazamiento
        list_frame = tk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Área de listbox y barra de desplazamiento
        self.listbox = tk.Listbox(list_frame, width=40, height=15, font=("Helvetica", 10), selectbackground="#4a90e2", exportselection=0)
        self.scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Al hacer clic en un elemento de la lista, llama a la función show_names
        self.listbox.bind("<<ListboxSelect>>", self.show_names)

    def on_focus_in(self, event):
        """Borra el texto 'Search...' cuando el usuario hace clic en el cuadro de búsqueda."""
        if self.search_entry.get() == "Search...":
            self.search_var.trace_remove("write", self.trace_res)
            self.search_entry.delete(0, tk.END)
            self.trace_res = self.search_var.trace_add("write", self.filter_channels)

    def on_focus_out(self, event):
        """Restaura el texto 'Search...' si el cuadro de búsqueda está vacío cuando pierde el foco."""
        if self.search_entry.get() == "":
            self.search_var.trace_remove("write", self.trace_res)
            self.search_entry.insert(0, "Search...")
            self.trace_res = self.search_var.trace_add("write", self.filter_channels)
    
    def refresh_list_aux(self):
        """Refresca el fichero M3U"""
        # Recuperar M3U vía web en caso de que sea necesario
        popup = tk.Toplevel(self.root)
        popup.geometry("700x200")
        popup.title('Info')
        popup.attributes('-topmost', 'true')
        tk.Label(popup, text= "Updating your m3u list, please wait until this window is closed", font=("Helvetica", 12, "bold")).place(x=125,y=80)
        self.root.update()
        res = requests.get(self.conf['url']).text
        with open(self.m3u_path, 'w', encoding="utf8") as f:
            f.write(res)
            popup.destroy()
    
    def refresh_list(self):
        """Callback para cuando se pincha sobre el botón de refrescar"""
        self.refresh_list_aux()
        self.reset_search()
        self.show_streams()
    
    def reset_search(self):
        """Resetea el cuadro de búsqueda"""
        self.search_var.trace_remove("write", self.trace_res)
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Search...")
        self.trace_res = self.search_var.trace_add("write", self.filter_channels)

    def show_streams(self):
        """Muestra los Streams agrupados por 'title' y actualiza el indicador."""
        self.current_group = None
        self.show_grouped_channels("Streams")
        self.category_label.config(text="Selected: Streams", fg="#4a90e2")  # Cambiar texto y color del indicador

    def show_films_and_series(self):
        """Muestra las Films and Series agrupadas por 'title' y actualiza el indicador."""
        self.current_group = None
        self.show_grouped_channels("Films and Series")
        self.category_label.config(text="Selected: Films and Series", fg="#50e3c2")  # Cambiar texto y color del indicador

    def show_grouped_channels(self, category):
        """Muestra los títulos de los grupos en la listbox."""
        
        # Resetear búsqueda
        if self.current_category:
            self.reset_search()
            
        self.listbox.delete(0, tk.END)  # Limpiar la listbox

        # Agrupar los canales por 'title'
        self.current_category = category
        self.grouped_channels = self.channels[category]
        
        # Añadir los títulos de los grupos a la listbox
        for title in self.grouped_channels:
            self.listbox.insert(tk.END, title)

    def filter_channels(self, *args):
        """Filtra los canales según el texto del buscador."""
        filter_text = self.search_var.get().lower()
        if filter_text == "search...":
            return

        self.listbox.delete(0, tk.END)  # Limpiar la listbox
        
        # Filtrar los canales en base al texto de búsqueda
        if not self.current_group:
            # Filtro cuando no hemos pinchado en ninguna categoría
            for i in self.grouped_channels:
                if filter_text in i.lower():
                    self.listbox.insert(tk.END, i)
                    continue
                for j in self.grouped_channels[i]:
                    if filter_text in j.lower():
                        self.listbox.insert(tk.END, i)
                        break
        else:
            # Filtro cuando estamos en una categoría
            for i in self.grouped_channels[self.current_group]:
                if filter_text in i.lower():
                    self.listbox.insert(tk.END, i)

    def show_names(self, event):
        """No hace nada al hacer clic en un canal. Solo pasa si es un grupo de canales."""
        selection = self.listbox.curselection()
        if not selection:
            return
        selected_title = self.listbox.get(selection[0])

        # Verifica si el clic es sobre un grupo (title) o un canal (name)
        if selected_title in self.grouped_channels:
            self.current_group = selected_title
            self.reset_search() # Resetear la búsqueda al abrir canales
            self.show_channel_list(selected_title)  # Solo se muestra la lista de canales si es un grupo de canales
        else:
            # Abrir el canal con VLC
            if self.player:
                # Matar si hay uno en ejecución
                self.player.kill()
            url = self.grouped_channels[self.current_group][selected_title]['url']
            self.player = subprocess.Popen([self.conf['vlc_path'], '--meta-title', selected_title, url])

    def show_channel_list(self, group_title):
        """Muestra los canales de un grupo (título) en la misma ventana."""
        self.listbox.delete(0, tk.END)  # Limpiar la listbox

        # Obtener los canales correspondientes al título del grupo
        channels = self.grouped_channels[group_title]
        for channel in channels:
            name = channels[channel].get("name", "Unnamed")
            self.listbox.insert(tk.END, name)

        # Actualizar la etiqueta de la categoría
        self.category_label.config(text=f"Channels in {group_title}")
