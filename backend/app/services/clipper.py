from ..models import Clip

def create_candidates(source, target_count: int, clip_length: int):
    # Draft placeholders only. Real detection requires an authorized local media asset
    # and transcript pipeline; never scrape arbitrary public YouTube URLs.
    labels = ["Strong opening insight", "Key takeaway", "High-energy moment", "Practical tip", "Memorable conclusion", "Audience question", "Unexpected detail", "Quick explainer"]
    return [Clip(source_id=source.id, title=labels[i % len(labels)], start_seconds=float(i * clip_length),
        end_seconds=float((i + 1) * clip_length), score=0.55, status="draft",
        description="Candidate slot. Attach authorized media and run the AI analysis/render worker before publishing.")
        for i in range(target_count)]
