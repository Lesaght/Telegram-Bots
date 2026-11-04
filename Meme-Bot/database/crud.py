from typing import Optional, Dict, Any
from datetime import datetime
from database.client import supabase


async def get_or_create_user(user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
    response = supabase.table('users').select('*').eq('id', user_id).maybeSingle().execute()

    if response.data:
        return response.data

    user_data = {
        'id': user_id,
        'username': username,
        'is_moderator': False,
        'is_banned': False
    }

    response = supabase.table('users').insert(user_data).execute()
    return response.data[0]


async def add_new_meme(file_id: str, user_id: int) -> Dict[str, Any]:
    meme_data = {
        'file_id': file_id,
        'user_id': user_id,
        'status': 'PENDING'
    }

    response = supabase.table('memes').insert(meme_data).execute()
    return response.data[0]


async def get_random_approved_meme() -> Optional[Dict[str, Any]]:
    response = supabase.table('memes').select('*').eq('status', 'APPROVED').execute()

    if not response.data:
        return None

    import random
    return random.choice(response.data)


async def update_meme_status(meme_id: int, status: str, moderator_id: int) -> Dict[str, Any]:
    update_data = {
        'status': status,
        'moderated_at': datetime.utcnow().isoformat(),
        'moderated_by': moderator_id
    }

    response = supabase.table('memes').update(update_data).eq('id', meme_id).execute()
    return response.data[0] if response.data else {}


async def update_or_create_rating(meme_id: int, user_id: int, value: int) -> Dict[str, Any]:
    existing = supabase.table('ratings').select('*').eq('meme_id', meme_id).eq('user_id', user_id).maybeSingle().execute()

    if existing.data:
        response = supabase.table('ratings').update({'value': value}).eq('id', existing.data['id']).execute()
        return response.data[0]

    rating_data = {
        'meme_id': meme_id,
        'user_id': user_id,
        'value': value
    }

    response = supabase.table('ratings').insert(rating_data).execute()
    return response.data[0]


async def is_user_moderator(user_id: int) -> bool:
    response = supabase.table('users').select('is_moderator').eq('id', user_id).maybeSingle().execute()
    return response.data.get('is_moderator', False) if response.data else False


async def is_user_banned(user_id: int) -> bool:
    response = supabase.table('users').select('is_banned').eq('id', user_id).maybeSingle().execute()
    return response.data.get('is_banned', False) if response.data else False


async def get_meme_by_id(meme_id: int) -> Optional[Dict[str, Any]]:
    response = supabase.table('memes').select('*').eq('id', meme_id).maybeSingle().execute()
    return response.data
