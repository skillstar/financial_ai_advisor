import os  
from fastapi import FastAPI  
from fastapi.middleware.cors import CORSMiddleware  
from contextlib import asynccontextmanager  

from app.api.routes import router  
from app.core.config import settings  
from app.db.session import db  
from app.core.logger import logger, setup_logging  

# 设置日志  
setup_logging()  

@asynccontextmanager  
async def lifespan(app: FastAPI):  
    # 启动时执行  
    logger.info("应用启动中...")  
    # 连接数据库  
    await db.connect()  
    logger.info("数据库连接成功")  
    
    yield  
    
    # 关闭时执行  
    await db.disconnect()  
    logger.info("应用关闭")  

# 创建FastAPI应用  
app = FastAPI(  
    title="黄金交易平台API",  
    description="现货黄金线上交易平台的API接口",  
    version="1.0.0",  
    lifespan=lifespan  
)  

# 配置CORS  
app.add_middleware(  
    CORSMiddleware,  
    allow_origins=["*"],  # 在生产环境中应该限制为具体的域名  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)  

# 添加路由  
app.include_router(router, prefix="/api")  

@app.get("/")  
async def root():  
    return {"message": "黄金交易平台API服务正在运行"}  

if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(  
        "app.main:app",   
        host=settings.API_HOST,   
        port=settings.API_PORT,  
        reload=settings.DEBUG  
    )  