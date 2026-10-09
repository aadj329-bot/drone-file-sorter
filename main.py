import os 
import shutil
from datetime import datetime

from modules.file_mgmt_module import FileManager
from modules.metadata_module import get_metadata
from modules.timestamp_module import get_timestamp
from modules.utils_module import parse_arguments, get_folder_path


def main():
    args = parse_arguments()
    
    if args.path:
        folder = args.path
    else:
        folder = get_folder_path()

    if not os.path.isdir(folder):
        print("Folder does not exist.")
        return

    # Log files
    undo_log_path = "undo_log.txt"
    human_log_path = "organizer_log.txt"

    def log(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        with open(human_log_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    # Undo Option (Oopsie)
    if args.undo:
        if not os.path.exists(undo_log_path):
            print("No undo log found. Nothing to undo.")
            return

        print("Undoing previous file move...")
        with open(undo_log_path, "r") as f:
            lines = f.readlines()
        for line in reversed(lines):
            src, dest = line.strip().split(" -> ", 1)
            if os.path.exists(dest):
                print(f"Moving back: {dest} -> {src}")
                shutil.move(dest, src)
        print("Undo complete.")
        return

    undo_log = open(undo_log_path, "w")
    main_folder = folder
    dry_run = args.dry_run

    all_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    total_files = len(all_files)
    processed = 0

    fn = FileManager(undo_log_path)

    for item in all_files:
        item_path = os.path.join(main_folder, item)
        fn.move_file(item_path, main_folder, dry_run, undo_log)

        processed += 1
        percent = (processed / total_files) * 100
        bar_length = 40
        filled = int(bar_length * processed / total_files)
        bar = "█" * filled + "-" * (bar_length - filled)

        print(f"\rProgress: |{bar}| {percent: 5.1f}% {processed}/{total_files}", end="")

    print("\nOrganization complete.")
    undo_log.close()


if __name__ == "__main__":
    main()