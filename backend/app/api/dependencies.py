from fastapi import Depends, HTTPException, status, Header  
from typing import Optional  
import logging  

logger = logging.getLogger(__name__)  

async def get_current_user(x_auth_token: Optional[str] = Header(None)):  
    """简化版用户认证 - 仅用于开发测试阶段"""  
    # 任何token都当作有效 (仅用于测试阶段)  
    if x_auth_token:  
        return {"id": 1, "username": "test_user"}  
    
    # 如果没有提供token，也返回测试用户 (简化版，仅用于开发)  
    return {"id": 1, "username": "test_user"}  