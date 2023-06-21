from fastapi import FastAPI

import api_signup
import api_signin
import api_reset_password
import api_uploader
import api_delete_file
import api_user_status
import api_ocr
import api_savedata
import api_dashborad_delete

app=FastAPI()

# @app.on_event("startup")
# async def startup_event():
#     # This function initializes the tasks dictionary when the application starts
#     app.state.tasks = {}


app.include_router(api_signup.router)
app.include_router(api_signin.router)
app.include_router(api_reset_password.router)
app.include_router(api_uploader.router)
app.include_router(api_delete_file.router)
app.include_router(api_user_status.router)
app.include_router(api_ocr.router)
app.include_router(api_savedata.router)
app.include_router(api_dashborad_delete.router)


@app.get('/')
def Intro():
    return {"Message":"Welcome to FatsAPI"}







