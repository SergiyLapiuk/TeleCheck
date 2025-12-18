from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.model import predict_with_voting
from app.services.telegram_client import get_posts_from_channel
from app.services.telegram_client import get_channel_info
import asyncio

router = APIRouter()

class ChannelInfoRequest(BaseModel):
    channels: List[str]

class ChannelInfo(BaseModel):
    username: str
    title: str
    photo_url: str


class AnalyzeRequest(BaseModel):
    channels: List[str]
    start_date: str
    end_date: str

class ChannelStats(BaseModel):
    channel: str
    harmful: int
    normal: int
    harmful_percent: float

class LabeledPost(BaseModel):
    channel: str
    post: str
    label: int

@router.post("/analyze", response_model=List[ChannelStats])
def analyze_posts(request: AnalyzeRequest):
    result = []
    for ch in request.channels:
        posts = asyncio.run(get_posts_from_channel(ch, request.start_date, request.end_date))
        harmful = 0
        normal = 0
        for post in posts:
            label = predict_with_voting(post)
            if label == 1:
                harmful += 1
            else:
                normal += 1

        total = harmful + normal
        harmful_percent = (harmful / total * 100) if total > 0 else 0.0

        result.append(ChannelStats(
            channel=ch,
            harmful=harmful,
            normal=normal,
            harmful_percent=round(harmful_percent, 2)
        ))

    return result


@router.post("/labeled-posts", response_model=List[LabeledPost])
def labeled_posts(request: AnalyzeRequest):
    labeled = []
    for ch in request.channels:
        posts = asyncio.run(get_posts_from_channel(ch, request.start_date, request.end_date))
        for post in posts:
            label = predict_with_voting(post)
            labeled.append(LabeledPost(
                channel=ch,
                post=post,
                label=label
            ))

    return labeled

@router.post("/channel-info", response_model=List[ChannelInfo])
async def channel_info(request: ChannelInfoRequest):
    tasks = [get_channel_info(ch) for ch in request.channels]
    results = await asyncio.gather(*tasks)
    return results
