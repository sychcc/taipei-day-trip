from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta, timezone
import os
from models.user import create_user, authenticate_user

jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM")


async def signup(request: Request):
    # 初始化
    try:
        # 抓資料
        data = await request.json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # 檢查沒有空值
        if not name or not email or not password:
            return JSONResponse(
                status_code=400,
                content={'error': True, 'message': '註冊失敗，欄位不能為空'}
            )

        # 建立使用者
        user_id = create_user(name, email, password)
        
        if user_id is None:
            return JSONResponse(
                status_code=400,
                content={'error': True, 'message': '註冊失敗，重複的email'}
            )
        
        return {"ok": True}
    except Exception as e:
        print(f"ERROR:{e}")
        return JSONResponse(
            status_code=500,
            content={'error': True, 'message': '伺服器內部錯誤'}
        )


async def login(request: Request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        if not email:
            return JSONResponse(
                status_code=400,
                content={'error': True, 'message': '註冊失敗，email不能為空'}
            )
        if not password:
            return JSONResponse(
                status_code=400,
                content={'error': True, 'message': '註冊失敗，password不能為空'}
            )

        # 驗證使用者
        user = authenticate_user(email, password)

        if user:
            # user存在就製作jwt的payload(放使用者資料)
            payload = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'exp': datetime.now(timezone.utc) + timedelta(days=7)
            }
            token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)
            return {"token": token}
        else:
            return JSONResponse(
                status_code=400,
                content={'error': True, 'message': '登入失敗，帳號或密碼錯誤'}
            )
    except Exception as e:
        print(f"Login Error:{e}")
        return JSONResponse(
            status_code=500,
            content={'error': True, 'message': '伺服器內部錯誤'}
        )


async def get_login_status(request: Request):
    # 從前端取得header中的authorization
    auth_header = request.headers.get('Authorization')
    print(f"收到標頭: {auth_header}")

    # null 表示未登入
    # token 範例 Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    if not auth_header or not auth_header.startswith('Bearer '):
        return {'data': None}
    
    try:
        # 提取token資料
        token = auth_header.split(' ')[1]

        # jwt decode
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])

        return {
            'data': {
                'id': payload["id"],
                'name': payload["name"],
                'email': payload["email"]
            }
        }
    except Exception as e:
        # token失效
        print(f"驗證失敗原因:{e}")
        return {'data': None}