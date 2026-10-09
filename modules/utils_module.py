import argparse
import os
from datetime import datetime


def parse_arguments():
    """
    Parses command-line arguments for organizing files by extension.
    
    Returns:
        argparse.Namespace: An object containing the parsed arguments
    """
    parser = argparse.ArgumentParser(description="Organize files by extension.")
    parser.add_argument("--path", type=str, help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Show potential actions without moving files")
    parser.add_argument("--undo", action="store_true", help="Undo the last organization run")
    return parser.parse_args()


def get_folder_path():
    """
    Opens a file dialog to select a folder to organize.
    
    Returns:
        str: The path of the selected folder.
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select a folder to organize")
    return folder
