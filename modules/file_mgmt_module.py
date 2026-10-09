import os
import shutil
from datetime import datetime
from modules.metadata_module import get_metadata
from modules.timestamp_module import get_timestamp
from modules.constrants_module import PHOTO_EDITED_EXT, PHOTO_JPG_EXT, PHOTO_RAW_EXT, VIDEO_EXT, LOG_EXT


class FileManager:
    def __init__(self, undo_log_path="undo_log.txt"):
        self.undo_log_path = undo_log_path
        self.undo_log = []

    def move_file(self, path, root_output, dry_run=False):
        """
        Manages file operations, including moving files to appropriate subfolders based on their metadata and timestamp.
        
        Attributes:
            undo_log_path (str): The path to the undo log file.
            undo_log (list): A list to store undo log entries.
        
        Methods:
            __init__(undo_log_path: str = "undo_log.txt): Initializes the FileManager with an optional undo log path.
            move_file(path: str, root_output: str, dry_run: bool = False): Moves a file to the appropriate subfolder 
            based on its metadata and timestamp.
            save_undo_log(): Saves the undo log to the specified file.
        """
        meta = get_metadata(path)
        ts = get_timestamp(meta)

        ext = meta["file"]["extension"]

        subfolder = ["Photos", "RAW"] if ext in PHOTO_RAW_EXT else \
                    ["Photos", "JPG"] if ext in PHOTO_JPG_EXT else \
                    ["Photos", "Edited"] if ext in PHOTO_EDITED_EXT else \
                    ["Videos"] if ext in VIDEO_EXT else \
                    ["Logs"] if ext in LOG_EXT else \
                    ["Misc"] 

        year = ts.strftime("%Y")
        month = ts.strftime("%Y-%m")
        day = ts.strftime("%Y-%m-%d")

        if meta["drone"]["flight_timestamp"]:
            ft = meta["drone"]["flight_timestamp"]
            flight_folder = f"{ft.strftime('%Y-%m-%d_%H-%M-%S')}_Flight"
        else:
            flight_folder = f"{day}_Flight01"

        dest = os.path.join(root_output, *subfolder, year, month, day, flight_folder)
        final_path = os.path.join(dest, os.path.basename(path))

        if os.path.exists(final_path):
            existing_meta = get_metadata(final_path)
            if existing_meta["file"]["hash_md5"] == meta["file"]["hash_md5"]:
                print(f"Duplicate detected (same file) -> SKIPPED: {path}")
                return
            base, extn = os.path.splitext(os.path.basename(path))
            counter = 1
            new_final = os.path.join(dest, f"{base}_{counter}{extn}")
            while os.path.exists(new_final):
                counter += 1
                new_final = os.path.join(dest, f"{base}_{counter}{extn}")
            final_path = new_final

        if dry_run:
            print(f"[DRY_RUN] Would move {path} to {final_path}")
            return

        try:
            shutil.move(path, final_path)
            self.undo_log.append(f"{path} -> {final_path}")
            print(f"Moved {path} -> {final_path}")
        except Exception as e:
            print(f"Error moving file: {e}")

    def save_undo_log(self):
        with open(self.undo_log_path, "w") as f:
            for entry in self.undo_log:
                f.write(f"{entry}\n")