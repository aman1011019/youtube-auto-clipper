"""Render a user-supplied authorized media file into a vertical Short."""
import subprocess
from pathlib import Path
def render_vertical(input_path:str,output_path:str,start:float,duration:float,ffmpeg:str="ffmpeg"):
 src=Path(input_path); dst=Path(output_path)
 if not src.is_file(): raise FileNotFoundError("Authorized input media file not found")
 dst.parent.mkdir(parents=True,exist_ok=True)
 cmd=[ffmpeg,"-y","-ss",str(start),"-i",str(src),"-t",str(duration),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920","-c:v","libx264","-preset","veryfast","-crf","22","-c:a","aac","-movflags","+faststart",str(dst)]
 subprocess.run(cmd,check=True,capture_output=True,text=True); return str(dst)
