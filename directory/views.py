from django.http import JsonResponse
from django.core.cache import cache
from api.models import EyeColor, Country, session
from sqlalchemy import exists
import uuid


def get_eye_colors(request):

    cache_key = request.GET.get('cache_key', '')
    data = cache.get(cache_key)

    if not data:
        data = []

        for eye_color in session.query(EyeColor).all():
            row = {}
            row['id'] = eye_color.id
            row['title'] = eye_color.title
            row['description'] = eye_color.description
            data.append(row)

        # Create new cache
        cache_key = uuid.uuid4().hex
        cache_time = 86400 * 5

        cache.set(cache_key, data, cache_time)

    print(cache.get(cache_key))

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'cache_key': cache_key,
        'data': data
    }

    return JsonResponse(response)


def get_countries(request):

    cache_key = request.GET.get('cache_key', '')
    data = cache.get(cache_key)

    if not data:
        data = []

        for country in session.query(Country).all():
            row = {}
            row['id'] = country.id
            row['title'] = country.title
            row['description'] = country.description
            data.append(row)

        # Create new cache
        cache_key = uuid.uuid4().hex
        cache_time = 86400 * 5

        cache.set(cache_key, data, cache_time)

    print(cache.get(cache_key))

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'cache_key': cache_key,
        'data': data
    }

    return JsonResponse(response)


def get_eye_color(eye_color_id=''):

    response = 'undefined'
    if not session.query(exists().where(EyeColor.id == eye_color_id)).scalar():
        return response

    eye_color = session.query(EyeColor).filter_by(id=eye_color_id).first()

    return eye_color.description


def get_country(country_id=''):
    response = 'undefined'
    if not session.query(exists().where(Country.id == country_id)).scalar():
        return response

    country = session.query(Country).filter_by(id=country_id).first()

    return country.description