from datetime import datetime


def get_timestamp(meta):
    """
    Returns the timestamp from the metadata if available, otherwise returns the file modification time.
    
    Args:
        meta (dict): The metadata dictionary containing the file's metadata.
        
    Returns:
        datetime: The timestamp or filr modification time"""
    if meta.get("timestamp"):
        return meta["timestamp"]
    elif meta.get("video", {}).get("creation_time"):
        try:
            vid_ts = meta["video"]["creation_time"].replace("Z", "+00.00")
            return datetime.fromisoformat(vid_ts)
        except Exception as e:
            print(F"Error parsing video timestamp:{e}")
            return None
        
    elif meta.get("drone", {}).get("flight_timestamp"):
        return meta["drone"]["flight_timestamp"]
    else:
        return meta["file"]["modified"]