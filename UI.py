import customtkinter
from tkinter import filedialog, messagebox, StringVar
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import json
import main  # Importer le fichier main


def on_drag_enter(event):
    event.widget.focus_force()
    return event.action


def on_drop(event):
    file_path.set(event.data)
    label.configure(text=event.data)


def browse_file():
    selected_file = filedialog.askopenfilename(
        filetypes=[
            ("GCode Files", "*.nc *.cnc *.ngc *.gcode *.tap"),
            ("All Files", "*.*"),
        ]
    )
    if selected_file:
        file_path.set(selected_file)
        label.configure(text=selected_file)


def generate_file():
    input_file = file_path.get()
    if not input_file:
        messagebox.showerror("Error", "No file selected")
        return

    output_file = filedialog.asksaveasfilename(
        defaultextension=".nc",
        filetypes=[
            ("GCode Files", "*.nc *.cnc *.ngc *.gcode *.tap"),
            ("All Files", "*.*"),
        ],
    )
    if not output_file:
        return

    probe_code = snippet_entry.get()  # Use the snippet from the entry
    pattern = pattern_entry.get()  # Get the pattern from the entry
    new_lines = main.inject_probe_z(input_file, output_file, probe_code, pattern)

    messagebox.showinfo("Success", "File generated successfully")
    open_folder_button.grid(row=5, column=0, columnspan=2, pady=10)
    open_folder_button.configure(
        command=lambda: main.open_folder(os.path.dirname(output_file))
    )

    # Afficher le G-code dans le visualiseur avec les numéros de ligne et colorer les parenthèses, lignes injectées et commandes
    with open(output_file, "r") as file:
        lines = file.readlines()
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    gcode_content = "".join(numbered_lines)

    # Créer et afficher la zone de visualisation du G-code
    gcode_text.pack(side=customtkinter.RIGHT, fill=customtkinter.BOTH, expand=True)
    gcode_text.delete(1.0, customtkinter.END)
    gcode_text.insert(customtkinter.END, gcode_content)

    # Colorer les parenthèses
    start_index = "1.0"
    while True:
        start_index = gcode_text.search("(", start_index, stopindex=customtkinter.END)
        if not start_index:
            break
        end_index = f"{start_index} + 1c"
        gcode_text.tag_add("paren", start_index, end_index)
        start_index = end_index

    start_index = "1.0"
    while True:
        start_index = gcode_text.search(")", start_index, stopindex=customtkinter.END)
        if not start_index:
            break
        end_index = f"{start_index} + 1c"
        gcode_text.tag_add("paren", start_index, end_index)
        start_index = end_index

    # Colorer les lignes injectées
    for i, line in enumerate(numbered_lines):
        if probe_code in line:
            start_index = f"{i+1}.0"
            end_index = f"{i+1}.end"
            gcode_text.tag_add("injected", start_index, end_index)

    # Colorer les commandes G-code
    commands = ["T", "M", "G"]
    for command in commands:
        start_index = "1.0"
        while True:
            start_index = gcode_text.search(
                rf"\b{command}\d+",
                start_index,
                stopindex=customtkinter.END,
                regexp=True,
            )
            if not start_index:
                break
            end_index = gcode_text.index(f"{start_index} wordend")
            gcode_text.tag_add("command", start_index, end_index)
            start_index = end_index

    # Colorer les coordonnées X, Y, Z
    coordinates = {"X": "pink", "Y": "green", "Z": "purple"}
    for coord, color in coordinates.items():
        start_index = "1.0"
        while True:
            start_index = gcode_text.search(
                rf"{coord}-?\d+(\.\d+)?",
                start_index,
                stopindex=customtkinter.END,
                regexp=True,
            )
            if not start_index:
                break
            end_index = gcode_text.index(f"{start_index} wordend")
            gcode_text.tag_add(coord.lower(), start_index, end_index)
            start_index = end_index

    gcode_text.tag_config("paren", foreground="yellow")
    gcode_text.tag_config("injected", foreground="red")
    gcode_text.tag_config("command", foreground="lightblue")
    gcode_text.tag_config("x", foreground="pink")
    gcode_text.tag_config("y", foreground="green")
    gcode_text.tag_config("z", foreground="purple")

    # Redimensionner la fenêtre principale
    app.geometry("1250x850")


def toggle_mode():
    current_mode = customtkinter.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    customtkinter.set_appearance_mode(new_mode)


def change_language(lang):
    with open('languages.json', 'r', encoding='utf-8') as f:
        languages = json.load(f)
    
    if lang in languages:
        texts = languages[lang]
    else:
        texts = languages["English"]

    toggle_mode_button.configure(text=texts["toggle_mode"])
    label.configure(text=texts["drag_and_drop"])
    browse_button.configure(text=texts["browse_file"])
    generate_button.configure(text=texts["generate_file"])
    open_folder_button.configure(text=texts["open_folder"])
    snippet_label.configure(text=texts["snippet_label"])
    save_snippet_button.configure(text=texts["save_snippet"])
    pattern_label.configure(text=texts["pattern_label"])
    save_pattern_button.configure(text=texts["save_pattern"])


def change_text_color(widget, color):
    widget.configure(text_color=color)


# Configuration initiale
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")

# Création de l'application
app = TkinterDnD.Tk()
app.title("GCode Modifier")
app.geometry("550x700")
app.config(bg="#2e2e2e")

file_path = customtkinter.StringVar()

font = ("Dubai", 16)  # Définir une police plus lisible

frame = customtkinter.CTkFrame(app, bg_color="#2e2e2e", fg_color="#2e2e2e")
frame.pack(
    side=customtkinter.LEFT, pady=20, padx=20, fill=customtkinter.BOTH, expand=True
)

# Sélecteur de langue
languages = ["English", "Français", "ไทย"]
selected_language = StringVar(value=languages[0])
language_menu = customtkinter.CTkOptionMenu(
    app,
    values=languages,
    command=change_language,
    variable=selected_language,
    font=font,
)
language_menu.place(x=210, y=20)

# Bouton pour changer le mode
toggle_mode_button = customtkinter.CTkButton(
    app,
    text="Toggle Mode",
    command=toggle_mode,
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
toggle_mode_button.place(x=50, y=20)

# Cadre pour le glisser-déposer
dnd_frame = customtkinter.CTkFrame(
    frame,
    bg_color="#2e2e2e",
    fg_color="#1D1A29",
    border_width=2,
    width=500,
    height=150,
    corner_radius=10,
)
dnd_frame.pack(pady=60, padx=20, fill=customtkinter.BOTH, expand=True)

dnd_frame.drop_target_register(DND_FILES)
dnd_frame.dnd_bind("<<Drop>>", on_drop)
dnd_frame.dnd_bind("<<DragEnter>>", on_drag_enter)

# Étiquette pour le glisser-déposer
label = customtkinter.CTkLabel(
    dnd_frame,
    text="Drag and drop your GCode file here or click to browse",
    bg_color="#1D1A29",
    fg_color="#1D1A29",
    text_color="white",
    font=font,
)
label.place(relx=0.5, rely=0.3, anchor="center")

# Bouton pour parcourir les fichiers
browse_button = customtkinter.CTkButton(
    dnd_frame,
    text="Browse File",
    command=browse_file,
    fg_color="#1D1A29",
    text_color="white",
    corner_radius=10,
    border_width=2,
    font=font,
)
browse_button.place(relx=0.5, rely=0.7, anchor="center")

# Cadre pour les entrées et les boutons
entry_frame = customtkinter.CTkFrame(
    frame,
    bg_color="#2e2e2e",
    fg_color="#2e2e2e",
    corner_radius=10,
)
entry_frame.pack(pady=20, padx=20, fill=customtkinter.BOTH, expand=True)

# Étiquette et entrée pour le snippet
snippet_label = customtkinter.CTkLabel(
    entry_frame,
    text="Snippet to Inject:",
    bg_color="#2e2e2e",
    fg_color="#2e2e2e",
    text_color="white",
    font=font,
)
snippet_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

snippet_entry = customtkinter.CTkEntry(entry_frame, width=200, font=font)
snippet_entry.grid(row=0, column=1, pady=5, padx=10, sticky="w")

# Charger le snippet depuis le fichier JSON
main.load_snippet(snippet_entry)

# Étiquette pour le motif
pattern_label = customtkinter.CTkLabel(
    entry_frame,
    text="Pattern:",
    bg_color="#2e2e2e",
    fg_color="#2e2e2e",
    text_color="white",
    font=font,
)
pattern_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

# Entrée pour le motif
pattern_entry = customtkinter.CTkEntry(entry_frame, width=200, font=font)
pattern_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

# Charger le pattern depuis le fichier JSON
main.load_pattern(pattern_entry)

# Bouton pour enregistrer le snippet
save_snippet_button = customtkinter.CTkButton(
    entry_frame,
    text="Save Snippet",
    command=lambda: main.save_snippet(snippet_entry),
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
save_snippet_button.grid(row=2, column=0, pady=10, padx=10, sticky="w")

# Bouton pour enregistrer le motif
save_pattern_button = customtkinter.CTkButton(
    entry_frame,
    text="Save Pattern",
    command=lambda: main.save_pattern(pattern_entry),
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
save_pattern_button.grid(row=2, column=1, pady=10, padx=10, sticky="w")

# Bouton pour générer le fichier
generate_button = customtkinter.CTkButton(
    entry_frame,
    text="Generate File",
    command=generate_file,
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
generate_button.grid(row=3, column=0, columnspan=2, pady=20, padx=10)

# Bouton pour ouvrir le dossier une fois le fichier généré
open_folder_button = customtkinter.CTkButton(
    entry_frame,
    text="Open Folder",
    command=None,
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
open_folder_button.grid(row=4, column=0, columnspan=2, pady=20)
open_folder_button.grid_remove()  # Hide initially

# Zone de visualisation du G-code, initialement cachée
gcode_text = customtkinter.CTkTextbox(
    app,
    bg_color="#2e2e2e",
    fg_color="#1D1A29",
    text_color="white",
    corner_radius=12,
    font=font
)
gcode_text.pack_forget()

# Lancer l'application
app.mainloop()
