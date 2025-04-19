from typing import List, Optional, Dict, Any  
import uuid  
from datetime import datetime  
import pymysql  
from app.db.session import db  
from app.core.logger import logger  
from app.core.config import settings 

# 会话相关操作  
async def create_conversation(user_id: int, title: str = "New Conversation") -> Dict:  
    """创建新的会话"""  
    try:  
        conversation_id = str(uuid.uuid4())  
        now = datetime.now().isoformat()  
        
        query = """  
        INSERT INTO conversations (id, user_id, title, created_at, updated_at)   
        VALUES (%s, %s, %s, %s, %s)  
        """  
        
        await db.execute(query, conversation_id, user_id, title, now, now)  
        
        return {  
            "id": conversation_id,  
            "user_id": user_id,  
            "title": title,  
            "created_at": now,  
            "updated_at": now  
        }  
    except Exception as e:  
        logger.error(f"创建会话失败: {e}")  
        raise  

async def get_conversation_by_id(conversation_id: str) -> Optional[Dict]:  
    """通过ID获取会话"""  
    try:  
        query = "SELECT * FROM conversations WHERE id = %s"  
        result = await db.execute(query, conversation_id, fetch=True)  
        return result  
    except Exception as e:  
        logger.error(f"获取会话失败: {e}")  
        raise  

async def list_conversations(user_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:  
    """获取用户的会话列表"""  
    try:  
        query = """  
        SELECT c.*, COUNT(m.id) as message_count   
        FROM conversations c  
        LEFT JOIN messages m ON c.id = m.conversation_id  
        WHERE c.user_id = %s  
        GROUP BY c.id  
        ORDER BY c.updated_at DESC  
        LIMIT %s OFFSET %s  
        """  
        
        results = await db.execute(query, user_id, limit, offset, fetchall=True)  
        return results or []  
    except Exception as e:  
        logger.error(f"获取会话列表失败: {e}")  
        raise  

async def update_conversation_title(conversation_id: str, title: str) -> bool:  
    """更新会话标题"""  
    try:  
        query = """  
        UPDATE conversations   
        SET title = %s, updated_at = %s  
        WHERE id = %s  
        """  
        
        now = datetime.now().isoformat()  
        await db.execute(query, title, now, conversation_id)  
        return True  
    except Exception as e:  
        logger.error(f"更新会话标题失败: {e}")  
        return False  

# 消息相关操作  
async def create_message(conversation_id: str, role: str, content: str, message_id: Optional[str] = None) -> Dict:  
    """创建新消息"""  
    try:  
        if not message_id:  
            message_id = str(uuid.uuid4())  
            
        now = datetime.now().isoformat()  
        
        query = """  
        INSERT INTO messages (id, conversation_id, role, content, created_at)  
        VALUES (%s, %s, %s, %s, %s)  
        """  
        
        await db.execute(query, message_id, conversation_id, role, content, now)  
        
        # 更新会话的更新时间  
        update_query = "UPDATE conversations SET updated_at = %s WHERE id = %s"  
        await db.execute(update_query, now, conversation_id)  
        
        return {  
            "id": message_id,  
            "conversation_id": conversation_id,  
            "role": role,  
            "content": content,  
            "created_at": now  
        }  
    except Exception as e:  
        logger.error(f"创建消息失败: {e}")  
        raise  

async def update_message(message_id: str, content: str) -> bool:  
    """更新消息内容"""  
    try:  
        query = "UPDATE messages SET content = %s WHERE id = %s"  
        await db.execute(query, content, message_id)  
        return True  
    except Exception as e:  
        logger.error(f"更新消息失败: {e}")  
        return False  

async def get_conversation_messages(conversation_id: str) -> List[Dict]:  
    """获取会话的所有消息"""  
    try:  
        query = """  
        SELECT * FROM messages   
        WHERE conversation_id = %s  
        ORDER BY created_at  
        """  
        
        results = await db.execute(query, conversation_id, fetchall=True)  
        return results or []  
    except Exception as e:  
        logger.error(f"获取会话消息失败: {e}")  
        raise  

# 添加同步版本的SQL执行函数  
def sync_execute_custom_query(sql_query: str):  
    """同步版本的SQL查询执行函数（专为CrewAI工具设计）"""  
    import pymysql  
    from app.core.config import settings  
    
    try:  
        # 安全检查  
        lower_query = sql_query.lower()  
        dangerous_keywords = ['delete', 'drop', 'truncate', 'alter', 'insert', 'update']  
        if any(word in lower_query for word in dangerous_keywords):  
            logger.warning(f"拦截危险SQL: {sql_query}")  
            return []  # 不执行危险操作，返回空结果  
            
        # 确保查询是SELECT语句  
        if not lower_query.strip().startswith('select'):  
            logger.warning(f"非SELECT语句: {sql_query}")  
            return []  # 非SELECT语句返回空结果  
        
        # 创建直接连接而不是使用连接池  
        conn = pymysql.connect(  
            host=settings.DB_HOST,  
            port=settings.DB_PORT,  
            user=settings.DB_USER,  
            password=settings.DB_PASSWORD,  
            db=settings.DB_NAME,  
            charset='utf8mb4',  
            cursorclass=pymysql.cursors.DictCursor  
        )  
        
        with conn.cursor() as cursor:  
            cursor.execute(sql_query)  
            results = cursor.fetchall()  
        
        conn.close()  
        return results  
        
    except Exception as e:  
        logger.error(f"同步SQL执行错误: {str(e)}")  
        raise  

# 保留原有的异步执行查询函数  
async def execute_custom_query(query: str, *args) -> List[Dict]:  
    """执行自定义SQL查询（异步版本）"""  
    try:  
        # 安全检查  
        lower_query = query.lower()  
        dangerous_keywords = ['delete', 'drop', 'truncate', 'alter', 'insert', 'update']  
        if any(word in lower_query for word in dangerous_keywords):  
            raise ValueError(f"不允许执行修改数据库的查询: 包含关键词 {[word for word in dangerous_keywords if word in lower_query]}")  
            
        # 确保查询是SELECT语句  
        if not lower_query.strip().startswith('select'):  
            raise ValueError("只允许执行SELECT查询")  
            
        # 执行查询  
        results = await db.execute(query, *args, fetchall=True)  
        return results or []  
    except Exception as e:  
        logger.error(f"执行自定义查询失败: {e}")  
        raise 