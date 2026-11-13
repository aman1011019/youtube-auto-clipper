def publish_video(clip):
    from fastapi import HTTPException
    if not clip.video_path:
        raise HTTPException(409, "No rendered video file is attached to this clip.")
    raise HTTPException(503, "YouTube OAuth/upload is not configured. Configure Google Cloud OAuth and encrypted token storage.")
