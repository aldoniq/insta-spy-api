from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stories import getId, getStories
app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/getStories")
async def Hello(username: str, cookies: str = None):
    print(username, "user")
    userId = getId(username,cookies)
    if userId is None:
        return {
            "status": 404,
            "detail": "User not found"
        }
    data = getStories(userId, cookies)
    if data != {}:
        return {
                "status": 200,
                "detail": "Loaded stories",
                "data":  data 
            }
    else:
        return {
                "status": 404,
                "detail": "Loaded stories",
                "data": data 
            }