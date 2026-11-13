from fastapi import APIRouter
router=APIRouter(tags=["settings"])
@router.get("/settings")
def settings(): return {"daily_target_min":3,"daily_target_max":5,"publishing_mode":"review_required","format":"9:16"}
