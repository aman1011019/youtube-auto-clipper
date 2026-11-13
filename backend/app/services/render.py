"""Render an authorized input video into a vertical Short with burned-in captions."""
import subprocess
from pathlib import Path

def _stamp(value:float)->str:
    ms=max(0,int(round(value*1000)))
    h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def render_vertical(input_path:str,output_path:str,start:float,duration:float,ffmpeg:str="ffmpeg",captions=None):
    src=Path(input_path); dst=Path(output_path)
    if not src.is_file(): raise FileNotFoundError("Authorized input media file not found")
    dst.parent.mkdir(parents=True,exist_ok=True)
    filters=["scale=1080:1920:force_original_aspect_ratio=increase","crop=1080:1920"]
    if captions:
        srt=dst.with_suffix(".srt")
        entries=[]
        for item in captions:
            a=max(0.0,float(item["start"])-start); b=min(duration,float(item["end"])-start)
            if b<=a: continue
            text=str(item["text"]).replace("-->","→").strip()
            if text: entries.append(f"{len(entries)+1}\n{_stamp(a)} --> {_stamp(b)}\n{text}\n")
        srt.write_text("\n".join(entries),encoding="utf-8")
        safe=str(srt.resolve()).replace("\\","/").replace(":","\\:").replace("'","\\'")
        filters.append(f"subtitles=filename='{safe}':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=130'")
    cmd=[ffmpeg,"-y","-ss",str(start),"-i",str(src),"-t",str(duration),"-vf",",".join(filters),"-c:v","libx264","-preset","veryfast","-crf","22","-c:a","aac","-movflags","+faststart",str(dst)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    return str(dst)
