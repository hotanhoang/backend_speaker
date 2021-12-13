import uvicorn
if __name__ == "__main__":
    uvicorn.run("server.app:app", host="128.199.194.183", port=5000, reload=True)