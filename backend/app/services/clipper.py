import os, re, uuid
from pathlib import Path
from ..models import Clip
from .render import render_vertical

HOOK_WORDS={"why","how","secret","mistake","important","best","worst","never","always","truth","surprising","because","imagine","remember","tip","warning","lesson","actually","finally","first"}

def _rank(text: str, speech_seconds: float) -> float:
    words=re.findall(r"[a-zA-Z']+",text.lower())
    if not words: return 0.0
    hooks=sum(1 for w in words if w in HOOK_WORDS)
    questions=text.count("?")
    emphasis=text.count("!")
    density=min(len(words)/max(speech_seconds,1),3.2)/3.2
    length=min(len(words)/70,1.0)
    return round(min(0.99,0.25 + hooks*0.045 + questions*0.06 + emphasis*0.025 + density*0.18 + length*0.12),3)

def create_candidates(source, target_count: int, clip_length: int):
    if not source.media_path or not Path(source.media_path).is_file():
        raise ValueError("Upload the authorized video file to this source before generating clips.")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("Speech AI is not installed. Rebuild the backend after installing requirements.") from exc

    model_name=os.getenv("WHISPER_MODEL","base")
    model=WhisperModel(model_name,device=os.getenv("WHISPER_DEVICE","cpu"),compute_type=os.getenv("WHISPER_COMPUTE_TYPE","int8"))
    segment_iter,info=model.transcribe(source.media_path,beam_size=5,vad_filter=True)
    segments=[]
    for seg in segment_iter:
        text=(seg.text or "").strip()
        if text: segments.append({"start":float(seg.start),"end":float(seg.end),"text":text})
    if not segments: raise ValueError("No speech was detected. Try a video with clear spoken audio.")
    duration=float(info.duration or segments[-1]["end"])
    window=min(float(clip_length),duration)
    if window<10: raise ValueError("The video is too short to create a Short.")

    candidates=[]
    # Candidate windows begin at transcript segment boundaries, so the clip starts near speech.
    seen=set()
    for seg in segments:
        start=max(0.0,min(seg["start"],max(0.0,duration-window)))
        key=round(start/3)
        if key in seen: continue
        seen.add(key)
        end=min(duration,start+window)
        inside=[x for x in segments if x["end"]>start and x["start"]<end]
        text=" ".join(x["text"] for x in inside).strip()
        if len(text.split())<12: continue
        candidates.append({"start":start,"end":end,"text":text,"score":_rank(text,end-start)})

    selected=[]
    for item in sorted(candidates,key=lambda x:x["score"],reverse=True):
        if any(abs(item["start"]-x["start"])<window*0.65 for x in selected): continue
        selected.append(item)
        if len(selected)>=target_count: break
    if not selected: raise ValueError("Not enough clear speech was found for clips of this length.")

    media_root=Path(os.getenv("MEDIA_DIR","/media"))/"clips"
    media_root.mkdir(parents=True,exist_ok=True)
    result=[]
    for idx,item in enumerate(sorted(selected,key=lambda x:x["start"])):
        output=media_root/f"short-{source.id}-{uuid.uuid4().hex[:10]}.mp4"
        render_vertical(source.media_path,str(output),item["start"],item["end"]-item["start"],os.getenv("FFMPEG_PATH","ffmpeg"))
        words=item["text"].split()
        title=" ".join(words[:8]).strip(" ,.!?") or f"Highlight {idx+1}"
        if len(title)>90: title=title[:87]+"..."
        result.append(Clip(source_id=source.id,title=title,start_seconds=round(item["start"],2),
            end_seconds=round(item["end"],2),score=item["score"],status="draft",video_path=str(output),
            transcript=item["text"],description=item["text"][:4500]))
    return result
