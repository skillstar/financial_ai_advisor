import aiomysql  
import redis.asyncio as aioredis  
from app.core.config import settings  
from app.core.logger import logger  

# Redis连接池  
async def get_redis_pool():  
    redis_pool = await aioredis.from_url(  
        settings.REDIS_URL,  
        encoding="utf-8",  
        decode_responses=True  
    )  
    return redis_pool  

# MySQL连接池  
async def get_mysql_pool():  
    try:  
        pool = await aiomysql.create_pool(  
            host=settings.DB_HOST,  
            port=settings.DB_PORT,  
            user=settings.DB_USER,  
            password=settings.DB_PASSWORD,  
            db=settings.DB_NAME,  
            autocommit=True,  
            minsize=1,  
            maxsize=10  
        )  
        logger.info("MySQL连接池创建成功")  
        return pool  
    except Exception as e:  
        logger.error(f"创建MySQL连接池失败: {e}")  
        raise  

# 数据库上下文管理器  
class Database:  
    def __init__(self):  
        self.mysql_pool = None  
        self.redis = None  
    
    async def connect(self):  
        self.mysql_pool = await get_mysql_pool()  
        self.redis = await get_redis_pool()  
        
    async def disconnect(self):  
        if self.mysql_pool:  
            self.mysql_pool.close()  
            await self.mysql_pool.wait_closed()  
        if self.redis:  
            await self.redis.close()  
    
    async def execute(self, query, *args, fetch=False, fetchall=False):  
        async with self.mysql_pool.acquire() as conn:  
            async with conn.cursor(aiomysql.DictCursor) as cursor:  
                await cursor.execute(query, args)  
                if fetch:  
                    return await cursor.fetchone()  
                elif fetchall:  
                    return await cursor.fetchall()  
                return None  

# 实例化数据库  
db = Database()  