# Drone File Organizer

Organizes drone photos and videos by date and file type.

## Features

- Separates RAW (.DNG) and edited (.JPG) images
- Sorts media by capture data
- Places video into dedicated folders
- Supports undo operations
- Supports dry-run operations

## Requirements

- Python 3.6 or higher
- Pillow
- subprocess
- tkinter

## Requirements Installation

```bash
pip install -r requirements.txt
```

### DRY-RUN Usage

```bash
python main.py --path~desired-folder --dry-run
```

### Usage

```bash
python main.py --path~desired-folder
```

### Undo

```bash
python main.py --path~desired-folder --undo
```

## Contributing

Feel free to submit issues and pull request to improve the script.
Contributions are welcome!
