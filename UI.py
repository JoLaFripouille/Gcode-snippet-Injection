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
    new_lines = main.inject_probe_z(input_file, output_file, probe_code)

    messagebox.showinfo("Success", "File generated successfully")
    open_folder_button.pack(pady=10)
    open_folder_button.configure(
        command=lambda: main.open_folder(os.path.dirname(output_file))
    )

    # Afficher le G-code dans le visualiseur avec les numéros de ligne et colorer les parenthèses, lignes injectées et commandes
    with open(output_file, "r") as file:
        lines = file.readlines()
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    gcode_content = "".join(numbered_lines)

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
    gcode_text.pack(side=customtkinter.RIGHT, fill=customtkinter.BOTH, expand=True)


def toggle_mode():
    current_mode = customtkinter.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    customtkinter.set_appearance_mode(new_mode)


def change_language(lang):
    if lang == "English":
        texts = {
            "toggle_mode": "Toggle Mode",
            "drag_and_drop": "Drag and drop your GCode file here or click to browse",
            "browse_file": "Browse File",
            "generate_file": "Generate File",
            "open_folder": "Open Folder",
            "snippet_label": "Snippet to Inject:",
            "save_snippet": "Save Snippet",
        }
    elif lang == "Français":
        texts = {
            "toggle_mode": "Changer de mode",
            "drag_and_drop": "Glissez-déposez votre fichier GCode ici ou cliquez pour parcourir",
            "browse_file": "Parcourir le fichier",
            "generate_file": "Générer le fichier",
            "open_folder": "Ouvrir le dossier",
            "snippet_label": "Snippet à injecter:",
            "save_snippet": "Enregistrer le snippet",
        }
    elif lang == "ไทย":
        texts = {
            "toggle_mode": "สลับโหมด",
            "drag_and_drop": "ลากและวางไฟล์ GCode ของคุณที่นี่หรือตคลิกเพื่อเรียกดู",
            "browse_file": "เลือกไฟล์",
            "generate_file": "สร้างไฟล์",
            "open_folder": "เปิดโฟลเดอร์",
            "snippet_label": "โค้ดที่จะฉีด:",
            "save_snippet": "บันทึกโค้ด",
        }

    toggle_mode_button.configure(text=texts["toggle_mode"])
    label.configure(text=texts["drag_and_drop"])
    browse_button.configure(text=texts["browse_file"])
    generate_button.configure(text=texts["generate_file"])
    open_folder_button.configure(text=texts["open_folder"])
    snippet_label.configure(text=texts["snippet_label"])
    save_snippet_button.configure(text=texts["save_snippet"])


# Configuration initiale
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

# Création de l'application
app = TkinterDnD.Tk()
app.title("GCode Modifier")
app.geometry("1100x850")
app.config(bg="#2e2e2e")

file_path = customtkinter.StringVar()

font = ("Segoe UI", 12)  # Définir une police plus lisible

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
language_menu.place(x=200, y=10)

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
toggle_mode_button.place(x=20, y=20)

# Cadre pour le glisser-déposer
dnd_frame = customtkinter.CTkFrame(
    frame,
    bg_color="#3e3e3e",
    fg_color="#3e3e3e",
    width=500,
    height=150,
    corner_radius=10,
)
dnd_frame.pack(pady=10, padx=10, fill=customtkinter.BOTH, expand=True)

dnd_frame.drop_target_register(DND_FILES)
dnd_frame.dnd_bind("<<Drop>>", on_drop)
dnd_frame.dnd_bind("<<DragEnter>>", on_drag_enter)

# Étiquette pour le glisser-déposer
label = customtkinter.CTkLabel(
    dnd_frame,
    text="Drag and drop your GCode file here or click to browse",
    bg_color="#3e3e3e",
    fg_color="#3e3e3e",
    text_color="white",
    font=font,
)
label.place(relx=0.5, rely=0.3, anchor="center")

# Bouton pour parcourir les fichiers
browse_button = customtkinter.CTkButton(
    dnd_frame,
    text="Browse File",
    command=browse_file,
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
browse_button.place(relx=0.5, rely=0.7, anchor="center")

# Étiquette et entrée pour le snippet
snippet_label = customtkinter.CTkLabel(
    frame,
    text="Snippet to Inject:",
    bg_color="#2e2e2e",
    fg_color="#2e2e2e",
    text_color="white",
    font=font,
)
snippet_label.pack(pady=10, padx=10, anchor="w")

snippet_entry = customtkinter.CTkEntry(frame, width=400, font=font)
snippet_entry.pack(pady=5, padx=10, anchor="w")

# Charger le snippet depuis le fichier JSON
main.load_snippet(snippet_entry)

# Bouton pour enregistrer le snippet
save_snippet_button = customtkinter.CTkButton(
    frame,
    text="Save Snippet",
    command=lambda: main.save_snippet(snippet_entry),
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
save_snippet_button.pack(pady=10, padx=10, anchor="w")

# Bouton pour générer le fichier
generate_button = customtkinter.CTkButton(
    frame,
    text="Generate File",
    command=generate_file,
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
generate_button.pack(pady=20)

# Bouton pour ouvrir le dossier une fois le fichier généré
open_folder_button = customtkinter.CTkButton(
    frame,
    text="Open Folder",
    command=None,
    fg_color="#4e4e4e",
    text_color="white",
    corner_radius=10,
    font=font,
)
open_folder_button.pack(pady=20)
open_folder_button.pack_forget()  # Hide initially

# Zone de visualisation du G-code
gcode_text = customtkinter.CTkTextbox(
    app, bg_color="#2e2e2e", fg_color="#2e2e2e", text_color="white", font=font
)
gcode_text.pack(side=customtkinter.RIGHT, fill=customtkinter.BOTH, expand=True)

# Lancer l'application
app.mainloop()
