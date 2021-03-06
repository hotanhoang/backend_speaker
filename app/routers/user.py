from fastapi import APIRouter,Depends, HTTPException,Header,Body,File, UploadFile,Form
from fastapi.encoders import jsonable_encoder

from typing import List, Optional
# from server.dependencies import get_token_header
from server.database import add_user, FindUserbyNumberPhone, update_user, user_helper
from models.user import UserSchema,UserLogin, ResponseModel, ErrorResponseModel, UpdateFeature, ResponseModelNodata

import jwt
from decouple import config
import hashlib

from core.voice_utils import extra_feature,compare_similarity

from core.API_GG.speech2text import main
import shutil
import subprocess
import torch
from scipy.io.wavfile import read
import os
import datetime;
import re


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="",
    tags=["user"],
    # dependencies=[Depends(get_token_header)],
)
# @router.get("/", tags=["user"],dependencies=[Depends(get_token_header)])
# x_token: Optional[str] = Header(None)
# async def get_user(id_user): 
#     return [{"username": "Rick"}, {"username": "Morty"}]


def PasswordToMd5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

# @router.post("/get_feature",tags=["user"])
# async def get_feature(file: UploadFile = File((...))):

#     with open("app/VoiceAudio/00001.wav", "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     out = subprocess.call(
#         'ffmpeg -i %s -ac 1 -ar 16000 -f wav %s'%("app/VoiceAudio/00001.wav"
#                                         ,"app/VoiceAudio/00003.wav"),
#         shell=True)
#     if out != 0:
#         return { "error" : "error"}
#     feature = extra_feature("app/VoiceAudio/00003.wav")
#     feature_numpy = feature.cpu().detach().numpy()
#     return feature_numpy.tolist()

@router.post("/user", tags=["user"])
async def register(user: UserSchema = Body(...)):
    new_user = jsonable_encoder(user)
    if len(new_user['password']) < 6:
        return ErrorResponseModel(201, "M???t kh???u ??t nh???t 6 k?? t???")
    new_user['password'] = PasswordToMd5(new_user['password'])
    result = await add_user(new_user)
    if result is False:
        return ErrorResponseModel(202, "S??? ??i???n tho???i ???? ???????c ????ng k??")
    return ResponseModel(result, "????ng k?? t??i kho???n th??nh c??ng")

@router.post("/login", tags=["user"])
async def user_login(user: UserLogin = Body(...)):
    user_login = jsonable_encoder(user)   
    result = await FindUserbyNumberPhone(user_login)
    if result is None:
        return ErrorResponseModel(404, "S??? ??i???n tho???i ch??a ???????c ????ng k??")

    if PasswordToMd5(user_login['password']) != result['password']:
        return ErrorResponseModel(204, "M???t kh???u kh??ng ????ng")

    jwt_token = jwt.encode(user_helper(result),SECRET_KEY)
    result['token_code'] = jwt_token.decode('utf-8')

    result_update = await update_user(result)
    if result_update: 
        return ResponseModel({
            "id_token" : jwt_token
        }, "Login Successfully")
    else : 
        return ErrorResponseModel(102, "M???t k???t n???i t???i CSDL")

@router.post("/update_feature", tags=["user"])
async def update_feature(audio: UploadFile = File(...) ,number_phone: str = Form(...)):
    try:
        ts = datetime.datetime.now().timestamp()
        with open("app/VoiceFeature/"+number_phone+"_"+str(ts)+".mp4","wb") as buffer:
            shutil.copyfileobj(audio.file,buffer)

        out = subprocess.call(
            'ffmpeg -i %s -ac 1 -ar 16000 -f wav %s' % ("app/VoiceFeature/"+number_phone+"_"+str(ts)+".mp4"
                                                    , "app/VoiceFeature/"+number_phone+"_"+str(ts)+".wav"),
        shell=True)
        if out != 0:
            return ErrorResponseModel(400, "L???i d??? li???u kh??ng h???p l???")

        os.remove("app/VoiceFeature/"+number_phone+"_"+str(ts)+".mp4")

        sr, audio_1 = read("app/VoiceFeature/"+number_phone+"_"+str(ts)+".wav")
        # sr, audio_1 = read(audio.file)
        if len(audio_1) < 16000 * 1.6:
            return ErrorResponseModel(208, "??m thanh ch??a ?????t y??u c???u")

        result = extra_feature("app/VoiceFeature/"+number_phone+"_"+str(ts)+".wav")

        # result = extra_feature(audio=audio.file)
        result = result.detach().cpu().numpy().tolist()
        
        userbynumberphone = await FindUserbyNumberPhone({
            "number_phone" : number_phone
        })

        if userbynumberphone is None:
            return ErrorResponseModel(404, "S??? ??i???n tho???i ch??a ???????c ????ng k??")

        userbynumberphone['feature'] = result
        result_update = await update_user(userbynumberphone)

        if result_update: 
            return ResponseModel({},"????ng k?? x??c th???c b???ng ??m thanh th??nh c??ng")
        else : 
            return ErrorResponseModel(102, "M???t k???t n???i t???i CSDL")

    except Exception as err:
        print('err',err)
        return ErrorResponseModel(400, "L???i d??? li???u kh??ng h???p l???")

@router.post("/login_with_audio", tags=["user"])
async def login_with_audio(audio: UploadFile = File(...) ,number_phone: str = Form(...)):
    try:
        ts = datetime.datetime.now().timestamp()
        with open("app/VoiceLogin/"+number_phone+"_"+str(ts)+".mp4","wb") as buffer:
            shutil.copyfileobj(audio.file,buffer)
        out = subprocess.call(
            'ffmpeg -i %s -ac 1 -ar 16000 -f wav %s' % ("app/VoiceLogin/"+number_phone+"_"+str(ts)+".mp4"
                                                    , "app/VoiceLogin/"+number_phone+"_"+str(ts)+".wav"),
        shell=True)
        if out != 0:
            ResponseModelNodata(400, "L???i d??? li???u kh??ng h???p l???")

        os.remove("app/VoiceLogin/"+number_phone+"_"+str(ts)+".mp4")

        # Ki???m tra ch???t l?????ng file audio
        sr, audio_1 = read("app/VoiceLogin/"+number_phone+"_"+str(ts)+".wav")
        # sr, audio_1 = read(audio.file)
        if len(audio_1) < 16000 * 1.6:
            # print('len(audio)',len(audio_1))
            return ResponseModelNodata(208, "??m thanh ch??a ?????t y??u c???u")

        # Tr??ch tr???n ?????c tr??ng ??m thanh
        result = extra_feature("app/VoiceLogin/"+number_phone+"_"+str(ts)+".wav")
        # result = extra_feature(audio=audio.file)
        # T??m user theo s??? ??t
        userbynumberphone = await FindUserbyNumberPhone({
            "number_phone" : number_phone
        })
        if userbynumberphone is None:
            return ResponseModelNodata(404, "S??? ??i???n tho???i ch??a ???????c ????ng k??")

        # K???t qu??? tr??? v??? khi so s??nh 2 ?????c tr??ng
        result_predict = compare_similarity(result,torch.Tensor(userbynumberphone['feature']))
        # print('result_predict',result_predict)
        if result_predict is False:
            return ResponseModelNodata(406, "T??? ch???i truy c???p")

        # L??u file ??m thanh
        # with open("app/VoiceAudio/"+number_phone+".wav","wb") as buffer:
        #     shutil.copyfileobj(audio.file,buffer)

        # sub file ??m thanh
        sub = main("app/VoiceLogin/"+number_phone+"_"+str(ts)+".wav")
        # print('sub',sub)
        str_sub = ""        
        if(len(sub) != 0):
            for item in sub:
                if(item is not None):
                    str_sub += re.sub(r"\s+", "", item, flags=re.UNICODE)
        # print('str_sub',str_sub)
        
        jwt_token = jwt.encode(user_helper(userbynumberphone),SECRET_KEY)
        userbynumberphone['token_code'] = jwt_token.decode('utf-8')

        # os.remove("app/VoiceLogin/"+number_phone+"_"+str(ts)+".wav")
        # update tocken ID
        result_update = await update_user(userbynumberphone)
        if result_update: 
            return ResponseModel({
                "id_token" : jwt_token,
                "sub" : str_sub,
            },"Veryfi Successfully")
        else : 
            return ResponseModelNodata(102, "M???t k???t n???i t???i CSDL")

    except Exception as err:
        # print('err',err)
        return ResponseModelNodata(400, "L???i d??? li???u kh??ng h???p l???")

@router.post("/speech_to_text", tags=["user"])
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        with open("app/VoiceLogin/test.mp4","wb") as buffer:
            shutil.copyfileobj(audio.file,buffer)
            sub = main("app/VoiceLogin/test.mp4")
            os.remove("app/VoiceLogin/test.mp4")
            str_sub = ""        
            if(len(sub) != 0):
                for item in sub:
                    if(item is not None):
                        str_sub += f' {item}'
                return ResponseModel({
                        "sub" : str_sub,
                    },"Sub Successfully")
            else : 
                return ResponseModelNodata(404, "Sub Fail")
    except Exception as err:
        return ResponseModelNodata(400, "L???i d??? li???u kh??ng h???p l???")

