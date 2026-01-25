from fastapi import Query
from typing import Optional
from models.attraction import get_attractions, get_attraction_by_id, get_categories, get_mrts


async def show_attractions(
    page: int = Query(0, ge=0),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
):
    page_size = 8
    rows = get_attractions(page, page_size, category, keyword)
    
    if isinstance(rows, dict) and rows.get("error"):
        return rows
    
    # return json format
    data = []
    for row in rows:
        images = row['file'].split(',') if row['file'] else []
        mrt_str = row['MRT'] or ""
        mrt_value = mrt_str.split('/')[0].strip() if mrt_str else None
        data.append({
            'id': row['_id'],
            'name': row['name'],
            "category": row['CAT'],
            "description": row['description'],
            "address": row['address'],
            "transport": row['direction'],
            'mrt': mrt_value,
            "lat": row['latitude'],
            'lng': row['longitude'],
            "images": images,
        })
    
    next_page = page + 1 if len(data) == page_size else None
    
    return {
        'nextPage': next_page,
        'data': data
    }


async def attraction_id_data(attractionId: int):
    rows = get_attraction_by_id(attractionId)
    
    if isinstance(rows, dict) and rows.get("error"):
        return rows
    
    # return json format
    if not rows:
        return {
            "error": True,
            "message": "No this attraction id"
        }
    
    row = rows[0]
    images = row['file'].split(',') if row['file'] else []
    mrt_str = row['MRT'] or ""
    mrt_value = mrt_str.split('/')[0].strip() if mrt_str else None
    data = {
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


async def show_categories():
    rows = get_categories()
    
    if isinstance(rows, dict) and rows.get("error"):
        return rows
    
    # return json format
    if rows:
        data = []
        print(rows)
        for r in rows:
            data.append(r['CAT'])
    if data:
        return {"data": data}


async def show_mrts():
    rows = get_mrts()
    
    if isinstance(rows, dict) and rows.get("error"):
        return rows
    
    if rows:
        mrt_list = []
        for r in rows:
            mrt_list.append(r['MRT'])
        print(mrt_list)
    
    return {
        'data': mrt_list
    }
