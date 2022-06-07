from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil

from pill_detection import pillDetection

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### single image
@app.post("/pill_identifier")
async def root(image: UploadFile = File(...)):
    # image saving
    with open(f'{image.filename}', "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # running python with image path
    final_result = pillDetection(image.filename).main()
    return {"url_link":final_result}

# ### multi images
# @app.post("/multi_pill_identifier")
# async def multi(files: List[UploadFile] = File(...)):
#     for image in files:
#         with open(f'{image.filename}', "wb") as buffer:
#             shutil.copyfileobj(image.file, buffer)
            
#     return {"file_name":'hi'}


# from printHi import jun # the script that has to be run

# @app.post('/pill_test') 
# def register_watchdog(file: UploadFile = File(...)):
# #     th = Thread(target=printHi, args=(file.filename))
# #     th.start()
#     asd = jun(file.filename)
#     return {"result": asd}
# #     return {"status": file.filename}