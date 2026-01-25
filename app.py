# from fastapi import *
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse,JSONResponse
# from typing import Annotated,Optional
# import mysql.connector
# import mysql.connector.pooling # 連線池模組
# import os
# import jwt
# import requests
# from datetime import datetime, timedelta,timezone
# from dotenv import load_dotenv
# app=FastAPI()
# # load enviroment variable
# load_dotenv()

# # create mysql database connection
# #建立全域連線池
# db_config={
# 	'user':os.getenv('DB_USER'),
# 	'password':os.getenv('DB_PASSWORD'),
# 	'host':os.getenv('DB_HOST'),
# 	'database':os.getenv('DB_DATABASE')
# }
# db_pool = mysql.connector.pooling.MySQLConnectionPool(
#     pool_name="mypool",
#     pool_size=10,
#     **db_config
# )
# def get_db_connection():
# 	return db_pool.get_connection()
# # def get_db_connection():
# #     return mysql.connector.connect(
# #         user=os.getenv('DB_USER'),
# #         password=os.getenv('DB_PASSWORD'),
# #         host=os.getenv('DB_HOST'),
# #         database=os.getenv('DB_DATABASE')
# #     )

# jwt_secret = os.getenv("JWT_SECRET")
# jwt_algorithm = os.getenv("JWT_ALGORITHM")


# # APIS

# # Attraction
# @app.get('/api/attractions')
# async def show_attractions(
# 	page:int=Query(0,ge=0),
# 	category:Optional[str] = None,
# 	keyword:Optional[str] = None,
# ):
# 	con=get_db_connection()
# 	cursor=con.cursor(dictionary=True)
# 	page_size=8
# 	sql="""
#         SELECT _id,name,CAT,description,address,direction,MRT,latitude,longitude,file
# 		FROM attractions    
#     """
# 	params=[]

# 	#if category exits:
# 	if category:
# 		sql+="WHERE CAT=%s"
# 		params.append(category)
	
# 	if keyword:
# 		if category:
# 			sql+="AND (name LIKE %s OR MRT LIKE %s)"
# 		else:
# 			sql+="WHERE (name LIKE %s OR MRT LIKE %s)"

# 		kw = f"%{keyword}%"
# 		params.extend([kw, kw])
    	
#     #page
# 	sql+="LIMIT %s OFFSET %s"
# 	params.extend([page_size,page*page_size])
	
# 	try:
# 		cursor.execute(sql,params)
# 		rows=cursor.fetchall()
# 	except Exception as e:
# 		return{"error": True, "message": "server database error"}
# 	finally:
# 		cursor.close()
# 		con.close()


# 	# return json format
# 	data=[]
# 	for row in rows:
# 		images=row['file'].split(',') if row['file'] else []
# 		mrt_str=row['MRT'] or ""
# 		# parts=mrt_str.split('/')
# 		# mrt_list=[]
# 		# for m in parts:
# 		# 	m=m.strip()
# 		# 	if m:
# 		# 		mrt_list.append(m)
# 		mrt_value = mrt_str.split('/')[0].strip() if mrt_str else None
# 		data.append({
# 			'id':row['_id'],
# 			'name':row['name'],
# 			"category":row['CAT'],
# 			"description":row['description'],
# 			"address":row['address'],
# 			"transport":row['direction'],
# 			'mrt':mrt_value,
# 			"lat":row['latitude'],
# 			'lng':row['longitude'],
# 			"images":images,
# 		}
# 		)
# 	next_page=page+1 if len(data)==page_size else None
	
# 	if data:
# 		return{
# 			'nextPage':next_page,
# 			'data':data
# 	}

# @app.get('/api/attraction/{attractionId}')
# async def attraction_id_data(attractionId:Annotated[int,None]):
	
# 	con=get_db_connection()
# 	cursor=con.cursor(dictionary=True)
# 	sql="""
#         SELECT _id,name,CAT,description,address,direction,MRT,latitude,longitude,file
# 		FROM attractions WHERE _id=%s;
#     """
# 	params=[attractionId]

# 	try:
# 		cursor.execute(sql,params)
# 		rows=cursor.fetchall()
# 	except Exception as e:
# 		return{"error": True, "message": "server database error"}
# 	finally:
# 		cursor.close()
# 		con.close()
		
# 	# return json format
# 	if not rows:
# 		return{
# 			"error": True,
#             "message": "No this attraction id"
# 		}
# 	row=rows[0]
# 	images=row['file'].split(',') if row['file'] else []
# 	mrt_str=row['MRT'] or ""
# 	mrt_value = mrt_str.split('/')[0].strip() if mrt_str else None
# 	data={
# 		"id": row["_id"],
#         "name": row["name"],
#         "category": row["CAT"],
#         "description": row["description"],
#         "address": row["address"],
#         "transport": row["direction"],
#         "mrt": mrt_value,
#         "lat": row["latitude"],
#         "lng": row["longitude"],
#         "images": images
# 		}
# 	return {"data": data}

# # Attraction Category
# @app.get('/api/categories')
# async def show_categories():
# 	con=get_db_connection()
# 	cursor=con.cursor(dictionary=True)
# 	sql="SELECT DISTINCT CAT FROM attractions"
	
# 	try:
# 		cursor.execute(sql)
# 		rows=cursor.fetchall()
# 	except Exception as e:
# 		return{"error": True, "message": "server database error"}
# 	finally:
# 		cursor.close()
# 		con.close()


# 	# return json format
# 	if rows:
# 		data=[]
# 		print(rows);
# 		for r in rows:
# 			data.append(r['CAT'])
# 	if data:
# 		return{"data":data}
	
# # MRT station
# @app.get('/api/mrts')
# async def show_mrts():
# 	con=get_db_connection()
# 	cursor=con.cursor(dictionary=True)
# 	sql="""
# 	SELECT MRT, COUNT(*) AS attraction_count 
# 	FROM attractions WHERE MRT IS NOT NULL AND MRT !='' 
# 	GROUP BY MRT 
# 	ORDER BY attraction_count DESC
# 	"""
	
# 	try:
# 		cursor.execute(sql)
# 		rows=cursor.fetchall()
# 	except Exception as e:
# 		return{"error": True, "message": "server database error"}
# 	finally:
# 		cursor.close()
# 		con.close()
# 	if rows:
# 		mrt_list=[]
# 		for r in rows:
# 			mrt_list.append(r['MRT'])
# 		print(mrt_list)
	
# 	return{
# 		'data':mrt_list
# 	}	


# # User
# @app.post('/api/user')
# async def signup(request:Request):
# 	#初始化
# 	con=None
# 	cursor=None
# 	try:
# 		#抓資料
# 		data=await request.json()
# 		name=data.get('name')
# 		email=data.get('email')
# 		password=data.get('password')

# 		#檢查沒有空值
# 		if not name or not email or not password:
# 			return JSONResponse(
# 				status_code=400,
# 				content={'error':True,'message':'註冊失敗，欄位不能為空'}

# 			)
# 		#連接資料庫
# 		con=get_db_connection()
# 		cursor=con.cursor(dictionary=True)

# 		# 檢查 Email 是否重複
# 		check_sql="SELECT id FROM user WHERE email=%s"
# 		cursor.execute(check_sql, (email,))
# 		existing_user = cursor.fetchone()

# 		if existing_user:
# 			return JSONResponse(
# 				status_code=400,
# 				content={'error':True,'message':'註冊失敗，重複的email'}
# 			)
		
# 		#存入新會員資料到資料庫
# 		insert_sql="INSERT INTO user(name,email,password) VALUES (%s,%s,%s) "
# 		cursor.execute(insert_sql,(name,email,password))
# 		con.commit()
# 		return {"ok": True}
# 	except Exception as e:
# 		print(f"ERROR:{e}")
# 		return JSONResponse(
# 			status_code=500,
# 			content={'error':True,'message':'伺服器內部錯誤'}
# 		)
# 	finally:
# 		if cursor:
# 			cursor.close()
# 		if con:
# 			con.close()

# @app.put('/api/user/auth')
# async def login(request:Request):
# 	cursor=None
# 	con=None
# 	try:
# 		data=await request.json()
# 		email=data.get('email')
# 		password=data.get('password')

# 		if not email:
# 			return JSONResponse(
# 				status_code=400,
# 				content={'error':True,'message':'註冊失敗，email不能為空'}
# 			)
# 		if not password:
# 			return JSONResponse(
# 				status_code=400,
# 				content={'error':True,'message':'註冊失敗，password不能為空'}
# 			)
# 		#連接資料庫
# 		con=get_db_connection()
# 		cursor=con.cursor(dictionary=True)

# 		check_sql="SELECT id,name,email FROM user WHERE email=%s AND password=%s"
# 		cursor.execute(check_sql,(email,password))
# 		user=cursor.fetchone()

# 		if user:
# 			#user存在就製作jwt的payload(放使用者資料)
# 			payload={
# 				'id':user['id'],
# 				'name':user['name'],
# 				'email':user['email'],
# 				'exp':datetime.now(timezone.utc) + timedelta(days=7)
# 			}
# 			token=jwt.encode(payload,jwt_secret , algorithm=jwt_algorithm)
# 			return {"token":token}
# 		else:
# 			return JSONResponse(status_code=400,content={'error':True,'message':'登入失敗，帳號或密碼錯誤'})	
# 	except Exception as e:
# 		print(f"Login Error:{e}")
# 		return JSONResponse(
# 				status_code=500,
# 				content={'error':True,'message':'伺服器內部錯誤'}
# 			)
# 	finally:
# 		if cursor:
# 			cursor.close()
# 		if con:
# 			con.close()

# @app.get('/api/user/auth')
# async def get_login_status(request:Request):
# 	#從前端取得header中的authorization
# 	auth_header=request.headers.get('Authorization')
# 	print(f"收到標頭: {auth_header}")

# 	#null 表示未登入
# 	#token 範例 Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# 	if not auth_header or not auth_header.startswith('Bearer '):
# 		return {'data':None}
	
# 	try:
# 		# 提取token資料
# 		token= auth_header.split(' ')[1]

# 		#jwt decode
# 		payload=jwt.decode(token,jwt_secret,algorithms=[jwt_algorithm])

# 		return{
# 			'data':{
# 				'id':payload["id"],
# 				'name':payload["name"],
# 				'email':payload["email"]	
# 			}
# 		}
# 	except Exception as e:
# 		#token失效
# 		print(f"驗證失敗原因:{e}")
# 		return {'data':None}


# # booking

# # 建立預定
# @app.post('/api/booking')
# async def create_booking(request: Request):
# 	auth_header=request.headers.get('Authorization')
# 	print(f"收到標頭: {auth_header}")
# 	if not auth_header or not auth_header.startswith('Bearer '):
# 		return {'error':True,'message':'未登入系統，拒絕存取'},403
# 	try:
# 		token= auth_header.split(' ')[1]
# 		payload=jwt.decode(token,jwt_secret,algorithms=[jwt_algorithm])
# 		user_id=payload["id"] #取得登入者的id
# 	except Exception as e:
# 		return{'error':True,'message':'token無效，請重新登入'},403
	
# 	#取得前端傳來的景點json資料
# 	try:
# 		body=await request.json()
# 		attraction_id=body.get("attractionId")
# 		date=body.get('date')
# 		time=body.get('time')
# 		price=body.get('price')
# 	except:
# 		return {'error':True,'message':'JSON格式錯誤'},400
# 	#確定資料都有填寫
# 	if not all([attraction_id,date,time,price]):
# 		return{'error':True,'message':'資料不完整'},400
	
# 	#沒問題就將景點資料存入資料庫
# 	con=get_db_connection()
# 	cursor=con.cursor(dictionary=True)
# 	sql="""
# INSERT INTO booking(user_id,attraction_id,date,time,price)
# VALUES(%s,%s,%s,%s,%s)
# ON DUPLICATE KEY UPDATE
# 	attraction_id=VALUES(attraction_id),
# 	date = VALUES(date),
#     time = VALUES(time),
#     price = VALUES(price);
# """
# 	params = [user_id, attraction_id, date, time, price]
# 	try:
# 		cursor.execute(sql,params)
# 		con.commit()
# 		return {"ok": True}
# 	except Exception as e:
# 		print(f"Database Error:{e}")
# 		return {'error':True,'message':'伺服器內部錯誤'},500
# 	finally:
# 		cursor.close()
# 		con.close()


# # 取得預定行程
# @app.get('/api/booking')
# async def get_booking(request:Request):
# 	auth_header=request.headers.get('Authorization')
# 	print(f"收到標頭: {auth_header}")
# 	if not auth_header or not auth_header.startswith('Bearer '):
# 		return {'error':True,'message':'未登入系統，拒絕存取'},403
# 	try:
# 		token= auth_header.split(' ')[1]
# 		payload=jwt.decode(token,jwt_secret,algorithms=[jwt_algorithm])
# 		user_id=payload["id"] #取得登入者的id
# 	except Exception as e:
# 		return{'error':True,'message':'token無效，請重新登入'},403


# # 連接資料庫取得預定行程
# #booking 的表格join attractions的名稱、圖片網址、地點
# 	con = get_db_connection()
# 	cursor=con.cursor(dictionary=True)

# 	sql="""
# SELECT 
# 	b.attraction_id, b.date, b.time, b.price,
# 	a.name, a.address, a.file
# FROM booking AS b
# INNER JOIN attractions AS a
# ON b.attraction_id=a.id
# WHERE b.user_id=%s
# """
# 	try:
# 		cursor.execute(sql,(user_id,))
# 		row=cursor.fetchone()
# 		#如果沒有預定資料，回傳data:null
# 		if not row:
# 			return{'data':None}
# 		#有資料
# 		return{
#         	"data": {
#             	"attraction": {
#                 	"id": row['attraction_id'],
#                 	"name": row['name'],
#                 	"address": row['address'],
#                 	"image": row['file'].split(',')[0]
#             	},
#             	"date": row['date'].strftime('%Y-%m-%d'),
#             	"time": row['time'],
#             	"price": row['price']
#         	}
#     	}
# 	except Exception as e:
# 		print(f"Database Error:{e}")
# 		return{'error':True,'message':'伺服器內部錯誤'},500
# 	finally:
# 		cursor.close()
# 		con.close()

# #刪除行程
# @app.delete('/api/booking')
# async def delete_booking(request: Request):
# 	auth_header = request.headers.get('Authorization')
# 	if not auth_header or not auth_header.startswith('Bearer '):
# 		return{'error':True,'message':'未登入系統，拒絕存取'},403
# 	try:
# 		token=auth_header.split(' ')[1]
# 		payload=jwt.decode(token,jwt_secret,algorithms=[jwt_algorithm])
# 		user_id=payload["id"] #取得登入者的id
# 	except Exception as e:
# 		return{'error':True,'message':'token無效，請重新登入'},403
	

# 	#連接資料庫刪除預定
# 	con = get_db_connection()
# 	cursor=con.cursor()

# 	#刪除的sql指令
# 	#根據user_id刪除
# 	sql='DELETE FROM booking WHERE user_id=%s'
# 	try:
# 		cursor.execute(sql,(user_id,))
# 		con.commit()
# 		return{'ok':True}
# 	except Exception as e:
# 		print(f"Database Error:{e}")
# 		return{'error':True,'message':'伺服器內部錯誤'},500
# 	finally:
# 		cursor.close()
# 		con.close()

# # order APIs

# #POST /api/orders
# # @app.post("/api/orders")
# # async def create_order(request: Request):
# #     # 驗證登入狀態 (完全照抄你原本 DELETE /api/booking 的驗證邏輯)
# #     auth_header = request.headers.get('Authorization')
# #     if not auth_header or not auth_header.startswith('Bearer '):
# #         return JSONResponse(status_code=403, content={'error': True, 'message': '未登入系統'})
# #     try:
# #         token = auth_header.split(' ')[1]
# #         payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
# #         user_id = payload["id"]
# #     except:
# #         return JSONResponse(status_code=403, content={'error': True, 'message': 'Token 無效'})

# #     # 取得前端傳來的資料
# #     data = await request.json()
# #     prime = data.get("prime")
# #     order_info = data.get("order")
    
# #     # 建立唯一的訂單編號
# #     order_number = datetime.now().strftime('%Y%m%d%H%M%S') + str(user_id)

# #     con = get_db_connection()
# #     cursor = con.cursor(dictionary=True)
# #     try:
# #         #建立訂單紀錄 (status: 1 是未付款)
# #         insert_sql = """
# #             INSERT INTO orders (
# #                 number, user_id, price, attraction_id, attraction_name, 
# #                 attraction_address, attraction_image, date, time, 
# #                 contact_name, contact_email, contact_phone, status
# #             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
# #         """
# #         cursor.execute(insert_sql, (
# #             order_number, user_id, order_info['price'], 
# #             order_info['trip']['attraction']['id'], order_info['trip']['attraction']['name'],
# #             order_info['trip']['attraction']['address'], order_info['trip']['attraction']['image'],
# #             order_info['trip']['date'], order_info['trip']['time'],
# #             order_info['contact']['name'], order_info['contact']['email'], order_info['contact']['phone']
# #         ))
# #         con.commit()

# #         tappay_url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        
# #         partner_key = os.getenv("TAPPAY_PARTNER_KEY")
# #         merchant_id = os.getenv("TAPPAY_MERCHANT_ID")
        
# #         tappay_headers = {
# #             "Content-Type": "application/json",
# #             "x-api-key": partner_key
# #         }
        
# #         tappay_body = {
# #             "prime": prime,
# #             "partner_key": partner_key,
# #             "merchant_id": merchant_id,
# #             "details": f"台北一日遊 - {order_number}",
# #             "amount": order_info['price'],
# #             "cardholder": {
# #                 "phone_number": order_info['contact']['phone'],
# #                 "name": order_info['contact']['name'],
# #                 "email": order_info['contact']['email']
# #             }
# #         }
        
# #         print(f"Partner Key: {partner_key}")
# #         print(f"Merchant ID: {merchant_id}")
# #         print(f"Amount: {order_info['price']}")
        
# #         tp_res = requests.post(tappay_url, json=tappay_body, headers=tappay_headers)
# #         tp_result = tp_res.json()
# #         print(tp_result)


# #         if tp_result.get("status") == 0:
# #             print("=" * 50)
# #             print(" 付款成功！TapPay status = 0")
# #             print(f" 訂單編號: {order_number}")
# #             print(f" 使用者 ID: {user_id}")
# #             print("=" * 50)
            
# #             # 更新訂單狀態
# #             cursor.execute("UPDATE orders SET status = 0 WHERE number = %s", (order_number,))
# #             print(" 訂單狀態已更新為已付款")
            
# #             # 刪除 booking
# #             print(f"  準備刪除 user_id={user_id} 的 booking...")
# #             cursor.execute("DELETE FROM booking WHERE user_id = %s", (user_id,))
# #             deleted_count = cursor.rowcount
# #             print(f"  實際刪除了 {deleted_count} 筆 booking 資料")
            
# #             # commit
# #             con.commit()
# #             print(" 資料庫 commit 完成")
# #             print("=" * 50)
            
# #             return {"data": {"number": order_number, "payment": {"status": 0, "message": "付款成功"}}}
# #         else:
# #             print(f" 付款失敗！TapPay status = {tp_result.get('status')}")
# #             return {"data": {"number": order_number, "payment": {"status": tp_result.get("status"), "message": "付款失敗"}}}

# #     except Exception as e:
# #         print(f"Error: {e}")
# #         return JSONResponse(status_code=500, content={'error': True, 'message': '伺服器內部錯誤'})
# #     finally:
# #         cursor.close()
# #         con.close()
# @app.post("/api/orders")
# async def create_order(request: Request):
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith('Bearer '):
#         return JSONResponse(status_code=403, content={'error': True, 'message': '未登入系統'})
#     try:
#         token = auth_header.split(' ')[1]
#         payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
#         user_id = payload["id"]
#     except:
#         return JSONResponse(status_code=403, content={'error': True, 'message': 'Token 無效'})

#     data = await request.json()
#     prime = data.get("prime")
#     order_info = data.get("order")
    
#     order_number = datetime.now().strftime('%Y%m%d%H%M%S') + str(user_id)

#     con = get_db_connection()
#     cursor = con.cursor(dictionary=True)
#     try:
#         insert_sql = """
#             INSERT INTO orders (
#                 number, user_id, price, attraction_id, attraction_name, 
#                 attraction_address, attraction_image, date, time, 
#                 contact_name, contact_email, contact_phone, status
#             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
#         """
#         cursor.execute(insert_sql, (
#             order_number, user_id, order_info['price'], 
#             order_info['trip']['attraction']['id'], order_info['trip']['attraction']['name'],
#             order_info['trip']['attraction']['address'], order_info['trip']['attraction']['image'],
#             order_info['trip']['date'], order_info['trip']['time'],
#             order_info['contact']['name'], order_info['contact']['email'], order_info['contact']['phone']
#         ))
#         con.commit()

#         tp_result = {"status": 0, "msg": "Success"}
#         print("模擬付款成功:", tp_result)

#         if tp_result.get("status") == 0:
#             print("付款成功")
#             cursor.execute("UPDATE orders SET status = 0 WHERE number = %s", (order_number,))
#             cursor.execute("DELETE FROM booking WHERE user_id = %s", (user_id,))
#             deleted_count = cursor.rowcount
#             print(f"刪除了 {deleted_count} 筆 booking")
#             con.commit()
#             return {"data": {"number": order_number, "payment": {"status": 0, "message": "付款成功"}}}
#         else:
#             return {"data": {"number": order_number, "payment": {"status": tp_result.get("status"), "message": "付款失敗"}}}

#     except Exception as e:
#         print(f"Error: {e}")
#         return JSONResponse(status_code=500, content={'error': True, 'message': '伺服器內部錯誤'})
#     finally:
#         cursor.close()
#         con.close()

# # GET /api/order/{orderNumber}
# @app.get("/api/order/{orderNumber}")
# async def get_order_details(orderNumber: str, request: Request):
#     con = get_db_connection()
#     cursor = con.cursor(dictionary=True)
#     try:
#         cursor.execute("SELECT * FROM orders WHERE number = %s", (orderNumber,))
#         row = cursor.fetchone()
#         if not row:
#             return {"data": None}
            
#         return {
#             "data": {
#                 "number": row["number"],
#                 "price": row["price"],
#                 "trip": {
#                     "attraction": {
#                         "id": row["attraction_id"],
#                         "name": row["attraction_name"],
#                         "address": row["attraction_address"],
#                         "image": row["attraction_image"]
#                     },
#                     "date": str(row["date"]),
#                     "time": row["time"]
#                 },
#                 "contact": {
#                     "name": row["contact_name"],
#                     "email": row["contact_email"],
#                     "phone": row["contact_phone"]
#                 },
#                 "status": row["status"]
#             }
#         }
#     finally:
#         cursor.close()
#         con.close()


from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Annotated
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化FastAPI
app = FastAPI()

# 匯入controllers
from controllers.attraction_controller import show_attractions, attraction_id_data, show_categories, show_mrts
from controllers.user_controller import signup, login, get_login_status
from controllers.booking_controller import create_booking_controller, get_booking_controller, delete_booking_controller
from controllers.order_controller import create_order_controller, get_order_details

# APIS

# Attraction
@app.get('/api/attractions')
async def attractions_route(
    page: int = Query(0, ge=0),
    category: str = None,
    keyword: str = None,
):
    return await show_attractions(page, category, keyword)

@app.get('/api/attraction/{attractionId}')
async def attraction_route(attractionId: Annotated[int, None]):
    return await attraction_id_data(attractionId)

@app.get('/api/categories')
async def categories_route():
    return await show_categories()

@app.get('/api/mrts')
async def mrts_route():
    return await show_mrts()

# User
@app.post('/api/user')
async def signup_route(request: Request):
    return await signup(request)

@app.put('/api/user/auth')
async def login_route(request: Request):
    return await login(request)

@app.get('/api/user/auth')
async def get_login_status_route(request: Request):
    return await get_login_status(request)

# Booking
@app.post('/api/booking')
async def create_booking_route(request: Request):
    return await create_booking_controller(request)

@app.get('/api/booking')
async def get_booking_route(request: Request):
    return await get_booking_controller(request)

@app.delete('/api/booking')
async def delete_booking_route(request: Request):
    return await delete_booking_controller(request)

# Order
@app.post("/api/orders")
async def create_order_route(request: Request):
    return await create_order_controller(request)

@app.get("/api/order/{orderNumber}")
async def get_order_route(orderNumber: str, request: Request):
    return await get_order_details(orderNumber, request)









app.mount("/static", StaticFiles(directory="static"), name="static")
# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")