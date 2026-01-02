from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,JSONResponse
from typing import Annotated
import mysql.connector
import os
import jwt
from datetime import datetime, timedelta,timezone
from dotenv import load_dotenv
app=FastAPI()
# load enviroment variable
load_dotenv()
# create mysql database connection
import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE')
    )

jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM")


# APIS

# Attraction
@app.get('/api/attractions')
async def show_attractions(
	page:int=Query(0,ge=0),
	category:str|None=None,
	keyword:str|None=None,
):
	con=get_db_connection()
	cursor=con.cursor(dictionary=True)
	page_size=8
	sql="""
        SELECT _id,name,CAT,description,address,direction,MRT,latitude,longitude,file
		FROM attractions    
    """
	params=[]

	#if category exits:
	if category:
		sql+="WHERE CAT=%s"
		params.append(category)
	
	if keyword:
		if category:
			sql+="AND (name LIKE %s OR MRT LIKE %s)"
		else:
			sql+="WHERE (name LIKE %s OR MRT LIKE %s)"

		kw = f"%{keyword}%"
		params.extend([kw, kw])
    	
    #page
	sql+="LIMIT %s OFFSET %s"
	params.extend([page_size,page*page_size])
	
	try:
		cursor.execute(sql,params)
		rows=cursor.fetchall()
	except Exception as e:
		return{"error": True, "message": "server database error"}
	finally:
		cursor.close()
		con.close()


	# return json format
	data=[]
	for row in rows:
		images=row['file'].split(',') if row['file'] else []
		mrt_str=row['MRT'] or ""
		# parts=mrt_str.split('/')
		# mrt_list=[]
		# for m in parts:
		# 	m=m.strip()
		# 	if m:
		# 		mrt_list.append(m)
		mrt_value = mrt_str.split('/')[0].strip() if mrt_str else None
		data.append({
			'id':row['_id'],
			'name':row['name'],
			"category":row['CAT'],
			"description":row['description'],
			"address":row['address'],
			"transport":row['direction'],
			'mrt':mrt_value,
			"lat":row['latitude'],
			'lng':row['longitude'],
			"images":images,
		}
		)
	next_page=page+1 if len(data)==page_size else None
	
	if data:
		return{
			'nextPage':next_page,
			'data':data
	}

@app.get('/api/attraction/{attractionId}')
async def attraction_id_data(attractionId:Annotated[int,None]):
	
	con=get_db_connection()
	cursor=con.cursor(dictionary=True)
	sql="""
        SELECT _id,name,CAT,description,address,direction,MRT,latitude,longitude,file
		FROM attractions WHERE _id=%s;
    """
	params=[attractionId]

	try:
		cursor.execute(sql,params)
		rows=cursor.fetchall()
	except Exception as e:
		return{"error": True, "message": "server database error"}
	finally:
		cursor.close()
		con.close()
		
	# return json format
	if not rows:
		return{
			"error": True,
            "message": "No this attraction id"
		}
	row=rows[0]
	images=row['file'].split(',') if row['file'] else []
	mrt_str=row['MRT'] or ""
	# parts=mrt_str.split('/')
	# mrt_list=[]
	# for m in parts:
	# 	m=m.strip()
	# 	if m:
	# 		mrt_list.append(m)
	mrt_value = mrt_str.split('/')[0].strip() if mrt_str else None
	data={
		"id": row["_id"],
        "name": row["name"],
        "category": row["CAT"],
        "description": row["description"],
        "address": row["address"],
        "transport": row["direction"],
        "mrt": mrt_value,
        "lat": row["latitude"],
        "lng": row["longitude"],
        "images": images
		}
	return {"data": data}

# Attraction Category
@app.get('/api/categories')
async def show_categories():
	con=get_db_connection()
	cursor=con.cursor(dictionary=True)
	sql="SELECT DISTINCT CAT FROM attractions"
	
	try:
		cursor.execute(sql)
		rows=cursor.fetchall()
	except Exception as e:
		return{"error": True, "message": "server database error"}
	finally:
		cursor.close()
		con.close()


	# return json format
	if rows:
		data=[]
		print(rows);
		for r in rows:
			data.append(r['CAT'])
	if data:
		return{"data":data}
	
# MRT station
@app.get('/api/mrts')
async def show_mrts():
	con=get_db_connection()
	cursor=con.cursor(dictionary=True)
	sql="""
	SELECT MRT, COUNT(*) AS attraction_count 
	FROM attractions WHERE MRT IS NOT NULL AND MRT !='' 
	GROUP BY MRT 
	ORDER BY attraction_count DESC
	"""
	
	try:
		cursor.execute(sql)
		rows=cursor.fetchall()
	except Exception as e:
		return{"error": True, "message": "server database error"}
	finally:
		cursor.close()
		con.close()
	if rows:
		mrt_list=[]
		for r in rows:
			mrt_list.append(r['MRT'])
		print(mrt_list)
	
	return{
		'data':mrt_list
	}	


# User
@app.post('/api/user')
async def signup(request:Request):
	#初始化
	con=None
	cursor=None
	try:
		#抓資料
		data=await request.json()
		name=data.get('name')
		email=data.get('email')
		password=data.get('password')

		#檢查沒有空值
		if not name or not email or not password:
			return JSONResponse(
				status_code=400,
				content={'error':True,'message':'註冊失敗，欄位不能為空'}

			)
		#連接資料庫
		con=get_db_connection()
		cursor=con.cursor(dictionary=True)

		# 檢查 Email 是否重複
		check_sql="SELECT id FROM user WHERE email=%s"
		cursor.execute(check_sql, (email,))
		existing_user = cursor.fetchone()

		if existing_user:
			return JSONResponse(
				status_code=400,
				content={'error':True,'message':'註冊失敗，重複的email'}
			)
		
		#存入新會員資料到資料庫
		insert_sql="INSERT INTO user(name,email,password) VALUES (%s,%s,%s) "
		cursor.execute(insert_sql,(name,email,password))
		con.commit()
		return {"ok": True}
	except Exception as e:
		print(f"ERROR:{e}")
		return JSONResponse(
			status_code=500,
			content={'error':True,'message':'伺服器內部錯誤'}
		)
	finally:
		if cursor:
			cursor.close()
		if con:
			con.close()

@app.put('/api/user/auth')
async def login(request:Request):
	cursor=None
	con=None
	try:
		data=await request.json()
		email=data.get('email')
		password=data.get('password')

		if not email:
			return JSONResponse(
				status_code=400,
				content={'error':True,'message':'註冊失敗，email不能為空'}
			)
		if not password:
			return JSONResponse(
				status_code=400,
				content={'error':True,'message':'註冊失敗，password不能為空'}
			)
		#連接資料庫
		con=get_db_connection()
		cursor=con.cursor(dictionary=True)

		check_sql="SELECT id,name,email FROM user WHERE email=%s AND password=%s"
		cursor.execute(check_sql,(email,password))
		user=cursor.fetchone()

		if user:
			#user存在就製作jwt的payload(放使用者資料)
			payload={
				'id':user['id'],
				'name':user['name'],
				'email':user['email'],
				'exp':datetime.now(timezone.utc) + timedelta(days=7)
			}
			token=jwt.encode(payload,jwt_secret , algorithm=jwt_algorithm)
			return {"token":token}
		else:
			return JSONResponse(status_code=400,content={'error':True,'message':'登入失敗，帳號或密碼錯誤'})	
	except Exception as e:
		print(f"Login Error:{e}")
		return JSONResponse(
				status_code=500,
				content={'error':True,'message':'伺服器內部錯誤'}
			)
	finally:
		if cursor:
			cursor.close()
		if con:
			con.close()

@app.get('/api/user/auth')
async def get_login_status(request:Request):
	#從前端取得header中的authorization
	auth_header=request.headers.get('Authorization')
	print(f"收到標頭: {auth_header}")

	#null 表示未登入
	#token 範例 Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
	if not auth_header or not auth_header.startswith('Bearer '):
		return {'data':None}
	
	try:
		# 提取token資料
		token= auth_header.split(' ')[1]

		#jwt decode
		payload=jwt.decode(token,jwt_secret,algorithms=[jwt_algorithm])

		return{
			'data':{
				'id':payload["id"],
				'name':payload["name"],
				'email':payload["email"]	
			}
		}
	except Exception as e:
		#token失效
		print(f"驗證失敗原因:{e}")
		return {'data':None}










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