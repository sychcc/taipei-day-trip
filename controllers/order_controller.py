from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
import os
from datetime import datetime
from models.order import create_order, update_order_status, get_order_by_number
from models.booking import delete_booking_by_user

jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM")


async def create_order_controller(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JSONResponse(status_code=403, content={'error': True, 'message': '未登入系統'})
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        user_id = payload["id"]
    except:
        return JSONResponse(status_code=403, content={'error': True, 'message': 'Token 無效'})

    data = await request.json()
    prime = data.get("prime")
    order_info = data.get("order")
    
    order_number = datetime.now().strftime('%Y%m%d%H%M%S') + str(user_id)

    try:
        # 建立訂單
        success = create_order(
            order_number, user_id, order_info['price'],
            order_info['trip']['attraction']['id'], order_info['trip']['attraction']['name'],
            order_info['trip']['attraction']['address'], order_info['trip']['attraction']['image'],
            order_info['trip']['date'], order_info['trip']['time'],
            order_info['contact']['name'], order_info['contact']['email'], order_info['contact']['phone']
        )
        
        if not success:
            return JSONResponse(status_code=500, content={'error': True, 'message': '伺服器內部錯誤'})

        # 模擬付款成功
        tp_result = {"status": 0, "msg": "Success"}
        print("模擬付款成功:", tp_result)

        if tp_result.get("status") == 0:
            print("付款成功")
            # 更新訂單狀態
            update_order_status(order_number, 0)
            # 刪除 booking
            delete_booking_by_user(user_id)
            print(f"刪除 booking")
            return {"data": {"number": order_number, "payment": {"status": 0, "message": "付款成功"}}}
        else:
            return {"data": {"number": order_number, "payment": {"status": tp_result.get("status"), "message": "付款失敗"}}}

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(status_code=500, content={'error': True, 'message': '伺服器內部錯誤'})


async def get_order_details(orderNumber: str, request: Request):
    row = get_order_by_number(orderNumber)
    
    if not row:
        return {"data": None}
    
    return {
        "data": {
            "number": row["number"],
            "price": row["price"],
            "trip": {
                "attraction": {
                    "id": row["attraction_id"],
                    "name": row["attraction_name"],
                    "address": row["attraction_address"],
                    "image": row["attraction_image"]
                },
                "date": str(row["date"]),
                "time": row["time"]
            },
            "contact": {
                "name": row["contact_name"],
                "email": row["contact_email"],
                "phone": row["contact_phone"]
            },
            "status": row["status"]
        }
    }