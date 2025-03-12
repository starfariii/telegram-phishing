import uvicorn, asyncio
from loader import *
from web_handlers.authorization_tg import *
from utils.webapp_func.auth_webapp import *
from loader import *
import logging
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "webapp_logs.log")

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,  
    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
    filemode="a", 
)


@app.get('/redir')
async def redirFunc(req: Request, type: str):

    logger.info(type)

    return templates.TemplateResponse("base_page.html", {"request": req, 'data_page': {'type': type}})

if __name__ == '__main__':    
    uvicorn.run(app, host='127.0.0.1', port=7777)