import hashlib
import os 
import subprocess
import json
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from modules.constrants_module import PHOTO_EDITED_EXT, PHOTO_JPG_EXT, PHOTO_RAW_EXT, VIDEO_EXT


def hash_file(path):
    """
    Hashes a file using MD5.
    
    Args:
        path (str): The path to the file to be hashed.
        
    Returns:
        str: The MD5 hash of the file of None if an error occurred
    """
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error hashing file: {e}")
        return None


def parse_exif(path, metadata):
    """
    Parses EXIF data from an image file and populates the metadata dictionary.
    
    Args:
        path (str): The path to the image file.
        metadata (dict): The metadata dictionary to be populated.
        
    Returns:
        None
    """
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return

            exif_data = {TAGS.get(k, k): v for k, v in exif.items()}

            for key in ("DateTimeOriginal", "CreateDate", "ModifyDate"):
                ts_str = exif_data.get(key)
                if ts_str:
                    try:
                        metadata["timestamp"] = datetime.strptime(ts_str, "%Y:%m:%d %H:%M:%S")
                        break
                    except Exception as e:
                        print(f"Error parsing timestamp {ts_str}: {e}")

            metadata["camera"]["model"] = exif_data.get("Model")
            metadata["camera"]["make"] = exif_data.get("Make")
            metadata["camera"]["lens"] = exif_data.get("LensModel")
            metadata["camera"]["iso"] = exif_data.get("ISOSpeedRating")
            metadata["camera"]["aperture"] = exif_data.get("FNumber")
            metadata["camera"]["shutter_speed"] = exif_data.get("ExposureTime")
            metadata["camera"]["focal_length"] = exif_data.get("FocalLength")

    except Exception as e:
        print(f"Error parsing EXIF: {e}")


def parse_video(path, metadata):
    """
    Parses metadata from a video file and populates the metadata dictionary.
    
    Args:
        path (str): The path to the video file.
        metadata (dict): The metadata dictionary to be populates.
        
    Returns:
        None
    """
    if not path.lower().endswith(('.mp4', '.mov', 'm4v')):
        return

    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
               "-show_format", "-show_streams", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        meta = json.loads(result.stdout)

        format_meta = meta.get("format", {})
        metadata["video"]["creation_time"] = format_meta.get("tags", {}).get("creation_time")
        metadata["video"]["duration"] = float(format_meta.get("duration", 0))
        metadata["video"]["bitrate"] = int(format_meta.get("bitrate", 0))

        for stream in meta.get("streams", []):
            if stream.get("codec_type") == "video":
                metadata["video"]["codec"] = stream.get("codec_name")
                metadata["video"]["resolution"] = f"{stream.get('width')}x{stream.get('height')}"
                break
    
    except Exception as e:
        print(f"Error parsing video: {e}")


def parse_srt(path, metadata):
    """Parses GPS and flight timestamp data from an SRT file and populates the metadata dictionary.
    
    Args:
        path (str): The path to the SRT file.
        metadata (dict): The metadata dictionary to be populated.
        
    Returns:
        None
    """
    if path.lower().endswith('.srt'):
        try:
            with open(path, "r", encoding="utf8", errors="ignore") as f:
                for line in f:
                    if "-->" in line:
                        ts = line.split("-->")[0].strip()
                        h, m, s = ts.split(":")
                        s = s.replace(",", ".")
                        base = datetime.fromtimestamp(os.path.getmtime(path))
                        metadata["drone"]["flight_timestamp"] = base.replace(hour=int(h), minute=int(m), second=int(float(s)))

                    if "GPS" in line:
                        parts = line.split(",")
                        for p in parts:
                            if "lat" in p:
                                metadata["drone"]["gps_lat"] = float(p.split("=")[1].strip())
                            if "lon" in p:
                                metadata["drone"]["gps_lon"] = float(p.split("=")[1].strip())
                            if "alt" in p:
                                metadata["drone"]["gps_alt"] = float(p.split("=")[1].strip())
        except Exception as e:
            print(f"Error parsing SRT: {e}")


def get_metadata(path):
    """
    Retrieves metadata for a file, including its type, creation timestamp, and other relevent details.
    
    Args:
        path (str): The path to the file.
        
    Returns:
        dict: A dictionary containing the metadata of the file.
    """
    metadata = {
        "timestamp": None,
        "gps": {"lat": None, "lon": None, "alt": None},
        "camera":{
            "model": None,
            "make": None,
            "lens": None,
            "iso": None,
            "aperture": None,
            "shutter_speed": None,
            "focal_length": None
         },
         "video": {
             "creation_time": None,
             "duration": None,
             "codec": None,
             "bitrate": None,
             "resolution": None
         },
         "drone": {
             "flight_timestamp": None,
             "gps_altitude": None,
             "gps_lat": None,
             "gps_lon": None,
             "flight_duration": None,
             "max_altitude": None,
             "max_distance":None
         },
         "file": {
             "size_bytes": os.path.getsize(path),
             "modified": datetime.fromtimestamp(os.path.getmtime(path)),
             "hash_md5": None,
             "extension": os.path.splitext(path)[1].lower()
         }
    }

    metadata["file"]["hash_md5"] = hash_file(path)
    if metadata["file"]["extension"] in PHOTO_RAW_EXT | PHOTO_JPG_EXT | PHOTO_EDITED_EXT:
        parse_exif(path, metadata)
    if metadata["file"]["extension"] in VIDEO_EXT:
        parse_video(path, metadata)
    parse_srt(path, metadata)

    return metadata