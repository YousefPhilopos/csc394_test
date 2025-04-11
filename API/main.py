from fastapi import FastAPI

app = FastAPI()

podcasts = ["Joe"]

@app.get("/name")
async def read_root():
    return podcasts


@app.post("/name")
def add_podcast(podcast):
    global podcasts
    podcasts.append(podcast)
    return podcasts

@app.delete("/name")
async def delete_string(index: int = 0):
    podcasts.pop(index)
    return podcasts
