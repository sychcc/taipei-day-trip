from fastapi import Request
import jwt
import os
from models.booking import create_booking, get_booking_by_user, delete_booking_by_user

jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM")


async def create_booking_controller(request: Request):
    auth_header = request.headers.get('Authorization')
    print(f"收到標頭: {auth_header}")
    if not auth_header or not auth_header.startswith('Bearer '):
        return {'error': True, 'message': '未登入系統,拒絕存取'}, 403
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        user_id = payload["id"]  # 取得登入者的id
    except Exception as e:
        return {'error': True, 'message': 'token無效,請重新登入'}, 403
    
    # 取得前端傳來的景點json資料
    try:
        body = await request.json()
        attraction_id = body.get("attractionId")
        date = body.get('date')
        time = body.get('time')
        price = body.get('price')
    except:
        return {'error': True, 'message': 'JSON格式錯誤'}, 400
    
    # 確定資料都有填寫
    if not all([attraction_id, date, time, price]):
        return {'error': True, 'message': '資料不完整'}, 400
    
    # 建立預訂
    success = create_booking(user_id, attraction_id, date, time, price)
    
    if success:
        return {"ok": True}
    else:
        return {'error': True, 'message': '伺服器內部錯誤'}, 500


async def get_booking_controller(request: Request):
    auth_header = request.headers.get('Authorization')
    print(f"收到標頭: {auth_header}")
    if not auth_header or not auth_header.startswith('Bearer '):
        return {'error': True, 'message': '未登入系統,拒絕存取'}, 403
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        user_id = payload["id"]  # 取得登入者的id
    except Exception as e:
        return {'error': True, 'message': 'token無效,請重新登入'}, 403

    # 取得預訂行程
    row = get_booking_by_user(user_id)
    
    # 如果沒有預訂資料,回傳data:null
    if not row:
        return {'data': None}
    
    # 有資料
    return {
        "data": {
            "attraction": {
                "id": row['attraction_id'],
                "name": row['name'],
                "address": row['address'],
                "image": row['file'].split(',')[0]
            },
            "date": row['date'].strftime('%Y-%m-%d'),
            "time": row['time'],
            "price": row['price']
        }
    }


async def delete_booking_controller(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {'error': True, 'message': '未登入系統,拒絕存取'}, 403
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        user_id = payload["id"]  # 取得登入者的id
    except Exception as e:
        return {'error': True, 'message': 'token無效,請重新登入'}, 403
    
    # 刪除預訂
    success = delete_booking_by_user(user_id)
    
    if success:
        return {'ok': True}
    else:
        return {'error': True, 'message': '伺服器內部錯誤'}, 500