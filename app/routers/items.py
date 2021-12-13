from fastapi import APIRouter,Depends, HTTPException

# router = APIRouter()
# from dependencies import get_token_header

router = APIRouter(
    prefix="/items",
    tags=["items"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)

@router.get("/", tags=["items"])
async def get_item():
    # raise HTTPException(status_code=404, detail="Item not found")
    return [{"username": "Rick"}, {"username": "Morty"}]

@router.post("/", tags=["items"])
async def add_item():
    return [{"username": "Rick"}, {"username": "Morty"}]
