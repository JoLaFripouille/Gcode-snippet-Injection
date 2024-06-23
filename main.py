import json
import os
import shutil
from tkinter import messagebox


def load_snippet(entry):
    try:
        with open("snippet.json", "r") as f:
            data = json.load(f)
            entry.delete(0, "end")
            entry.insert(0, data.get("snippet", ""))
    except FileNotFoundError:
        entry.delete(0, "end")
        entry.insert(0, "G38.2 Z-10 F100")  # Default value


def save_snippet(entry):
    snippet = entry.get()
    with open("snippet.json", "w") as f:
        json.dump({"snippet": snippet}, f)
    messagebox.showinfo("Success", "Snippet saved successfully")


def inject_probe_z(input_file, output_file, probe_code):
    with open(input_file, "r") as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.startswith("T") and line[1].isdigit():
            new_lines.append(probe_code + "\n")

    with open(output_file, "w") as file:
        file.writelines(new_lines)

    return new_lines  # Retourner les nouvelles lignes pour les identifier dans le visualiseur


def open_folder(folder_path):
    if os.name == "nt":  # Windows
        os.startfile(folder_path)
    elif os.name == "posix":  # macOS, Linux
        shutil.os.system(f'open "{folder_path}"')
