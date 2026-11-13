import json,os
from pathlib import Path
from fastapi import HTTPException

def _load_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from cryptography.fernet import Fernet,InvalidToken
    key=os.getenv("GOOGLE_TOKEN_ENCRYPTION_KEY")
    token_path=Path(os.getenv("TOKEN_FILE","/data/youtube-token.enc"))
    if not key or not token_path.exists():
        raise HTTPException(503,"Connect your YouTube channel from Publishing settings first.")
    try:
        payload=Fernet(key.encode()).decrypt(token_path.read_bytes()).decode()
        credentials=Credentials.from_authorized_user_info(json.loads(payload),scopes=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube.readonly"])
    except (InvalidToken,ValueError,TypeError):
        raise HTTPException(500,"Saved YouTube token could not be decrypted. Reconnect your channel.")
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token_path.write_bytes(Fernet(key.encode()).encrypt(credentials.to_json().encode()))
    if not credentials.valid:
        raise HTTPException(401,"YouTube authorization expired. Reconnect your channel.")
    return credentials

def publish_video(clip):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    media=Path(clip.video_path)
    if not media.is_file():
        raise HTTPException(409,"The rendered clip file is missing from server storage.")
    credentials=_load_credentials()
    try:
        youtube=build("youtube","v3",credentials=credentials,cache_discovery=False)
        body={"snippet":{"title":clip.title[:100],"description":(clip.description or "")[:5000],"categoryId":"22"},
              "status":{"privacyStatus":os.getenv("YOUTUBE_DEFAULT_PRIVACY","private"),"selfDeclaredMadeForKids":False}}
        upload=MediaFileUpload(str(media),mimetype="video/mp4",chunksize=8*1024*1024,resumable=True)
        request=youtube.videos().insert(part="snippet,status",body=body,media_body=upload)
        response=None
        while response is None:
            _,response=request.next_chunk()
        return {"video_id":response["id"],"url":"https://youtu.be/"+response["id"],"privacy_status":body["status"]["privacyStatus"]}
    except HttpError as exc:
        detail=getattr(exc,"content",b"").decode("utf-8","ignore")[:1000]
        raise HTTPException(502,"YouTube upload failed: "+detail)
