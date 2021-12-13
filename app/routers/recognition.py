from fastapi import APIRouter, File, UploadFile

from core.voice_utils import compare_similarity
from core.voice_utils import extra_feature

router = APIRouter(
    # prefix="/recognition",
    tags=["recognition"],
)

@router.post("/get_feature")
async def get_feature(audio: UploadFile = File(...)):
    try:
        result = extra_feature(audio=audio.file)
        result = result.detach().cpu().numpy().tolist()
        data = {'feature': result}
        return data
    except Exception as err:
        print(err)
        return {'error': 'error during get feature'}


@router.post("/compare")
async def compare(audio1: UploadFile = File(...), audio2: UploadFile = File(...)):
    try:
        result = compare_similarity(feat1=audio1.file, feat2=audio2.file)
        data = {'prediction': result}
        return data
    except Exception as err:
        print(err)
        return {'error': 'error during get feature'}
