from django.http import JsonResponse
from .views_users import check_access_token
from .models import User, Album, Photo, session
import os
import shutil
from api.tasks import save_photo, send_email


# Get user albums
def get_user_albums(user_id=''):

    albums_data = []

    for album in session.query(Album).filter_by(user_id=user_id).all():
        current_album = {}
        current_album['album_id'] = album.id
        current_album['album_title'] = album.album_title

        albums_data.append(current_album)

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'data': albums_data
    }

    return response


# Create album
def create_album(request_data, user_id=''):

    # Get album title
    album_title = request_data.get('album_title', '')

    if not album_title:

        response = {
            'status_code': 400,
            'status_message': 'Bad Request'
        }

        return response

    new_album = Album(album_title=album_title)

    user = session.query(User).filter_by(id=user_id).first()

    try:
        # Add new album
        user.albums.append(new_album)

        session.refresh(user)
        session.commit()

        album_id = str(new_album.id)

        response = {
            'status_code': 201,
            'status_message': 'Created',
            'album_id': album_id
        }

        return response

    except:

        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

        return response


# Get album data
def get_album_data(album_id=''):

    album = session.query(Album).filter_by(id=album_id).first()
    album_title = album.album_title

    user_id = str(album.user_id)

    album_photo_data = []

    # Get album photo
    for photo in session.query(Photo).filter_by(album_id=album_id).all():
        current_photo = {}
        photo_id = str(photo.id)
        current_photo['photo_id'] = photo_id
        current_photo['photo_caption'] = photo.photo_caption

        file_name_middle = "%s_600x600" % photo_id
        file_name_thumb = "%s_150x150" % photo_id

        path = "./media/%s/%s" % (user_id, album_id)

        path_for_url = "/media/%s/%s" % (user_id, album_id)

        for root, dirs, files in os.walk(path):
            for filename in files:

                photo_name, file_extension = filename.split('.')

                if photo_id == photo_name:
                    current_photo['original'] = "%s/%s.%s" % (path_for_url, photo_name, file_extension)

                if file_name_middle == photo_name:
                    current_photo['middle'] = "%s/%s.%s" % (path_for_url, photo_name, file_extension)

                if file_name_thumb == photo_name:
                    current_photo['thumb'] = "%s/%s.%s" % (path_for_url, photo_name, file_extension)

        album_photo_data.append(current_photo)

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'data': {
            'album_id': album_id,
            'album_title': album_title,
            'photo_data': album_photo_data
        }
    }

    return response


# Update album
def update_album(request_data, album_id=''):

    # Get album title
    new_album_title = request_data.get('album_title', '')

    if not new_album_title:
        response = {
            'status_code': 400,
            'status_message': 'Bad Request'
        }

        return response

    album = session.query(Album).filter_by(id=album_id).first()
    album.album_title = new_album_title

    album_id = str(album.id)

    session.commit()

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'album_id': album_id
    }

    return response


# Delete album
def delete_album(album_id='', user_id=''):

    # Get album
    album = session.query(Album).filter_by(id=album_id).first()

    try:

        # Delete related photo
        for photo in session.query(Photo).filter_by(album_id=album_id).all():
            session.delete(photo)

        session.delete(album)
        session.commit()

        path = "./media/%s/%s" % (user_id, album_id)

        # Delete album folder
        if os.path.exists(path):
            shutil.rmtree(path)

        response = {
            'status_code': 200,
            'status_message': 'OK'
        }

        return response

    except:
        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

        return response


def get_albums(request):

    access_token = request.GET.get('access_token', '')
    print('access_token', access_token)

    # Check access token
    check_token = check_access_token(access_token=access_token)
    if int(check_token['status_code']) != 200:
        return JsonResponse(check_token)

    user_id = check_token['user_id']

    # Get albums data
    if request.method == 'GET':
        response = get_user_albums(user_id=user_id)

    # Create album
    elif request.method == 'POST':
        request_data = request.POST
        response = create_album(request_data=request_data, user_id=user_id)

    else:
        response = {
            'status_code': '400',
            'status_message': 'Bad request'
        }

    return JsonResponse(response)


def get_album(request, album_id=''):

    access_token = request.GET.get('access_token', '')

    # Check access token
    check_token = check_access_token(access_token=access_token)
    if int(check_token['status_code']) != 200:

        return JsonResponse(check_token)

    current_user_id = check_token['user_id']

    # Check if the user has the right to access the album
    check_permission = check_album_permission(album_id=album_id, user_id=current_user_id)

    if int(check_permission['status_code']) != 200:
        return JsonResponse(check_permission)

    # Get album data (with photo)
    if request.method == 'GET':
        response = get_album_data(album_id=album_id)

    # Update album
    elif request.method == 'PUT':
        request_data = request.POST
        response = update_album(request_data=request_data, album_id=album_id)

    # Delete album
    elif request.method == 'DELETE':
        response = delete_album(album_id=album_id, user_id=current_user_id)

    else:
        response = {
            'status_code': 400,
            'status_message': 'Bad request'
        }

    return JsonResponse(response)


# Create photo
def create_photo(request, album_id=''):

    access_token = request.GET.get('access_token', '')
    image_data = request.POST.get('image_data', '')
    photo_caption = request.POST.get('photo_caption', '')

    # Check access token
    check_token = check_access_token(access_token=access_token)

    if int(check_token['status_code']) != 200:
        return JsonResponse(check_token)

    # Current user_id
    current_user_id = check_token['user_id']

    # Check image data
    if not image_data:
        response = {
            'status_code': 400,
            'status_message': 'Bad request'
        }
        return JsonResponse(response)

    # Check if the user has the right to access the album
    check_permission = check_album_permission(album_id=album_id, user_id=current_user_id)

    if int(check_permission['status_code']) != 200:
        return JsonResponse(check_permission)

    # Get user email
    current_user = session.query(User).filter_by(id=current_user_id).first()
    current_user_email = current_user.user_email

    # Create new photo
    new_photo = Photo(photo_caption=photo_caption)

    album = session.query(Album).filter_by(id=album_id).first()
    try:
        # Add new photo
        album.photo.append(new_photo)

        session.refresh(album)
        session.commit()

        photo_id = new_photo.id

        actions_on_create_photo = (save_photo.s(image_data=image_data, photo_id=photo_id, user_id=current_user_id, album_id=album_id,
                      email=current_user_email) | send_email.s()).apply_async()

        print(actions_on_create_photo.get())

        response = {
            'status_code': 201,
            'status_message': 'Created',
            'photo_id': photo_id
        }

    except:
        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

    return JsonResponse(response)


# Update photo
def update_photo(request_data, photo_id=''):

    new_photo_caption = request_data.get('photo_caption', '')
    if not new_photo_caption:
        response = {
            'status_code': 400,
            'status_message': 'Bad Request'
        }

        return response

    # Get photo
    photo = session.query(Photo).filter_by(id=photo_id).first()

    # Update photo
    photo.photo_caption = new_photo_caption

    session.commit()

    response = {
        'status_code': 200,
        'status_message': 'OK'
    }

    return response


# Delete photo
def delete_photo(photo_id='', album_id='', user_id=''):

    # Get photo
    photo = session.query(Photo).filter_by(id=photo_id).first()

    try:
        session.delete(photo)
        session.commit()

        path = "./media/%s/%s" % (user_id, album_id)

        if not os.path.exists(path):
            response = {
                'status_code': 400,
                'status_message': 'Bad request'
            }

            return response

        for root, dirs, files in os.walk(path):
            for filename in files:
                if photo_id in filename:
                    file = "%s/%s" % (path, filename)
                    os.remove(file)
                    print('deleted', filename)

        response = {
            'status_code': 200,
            'status_message': 'OK'
        }
        return response

    except:

        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

        return response


def get_photo(request, photo_id=''):

    access_token = request.GET.get('access_token', '')

    # Check access token
    check_token = check_access_token(access_token=access_token)

    if int(check_token['status_code']) != 200:
        return JsonResponse(check_token)

    # Current user_id
    current_user_id = check_token['user_id']

    # Check if the user has the right to access the photo
    check_permission = check_photo_permission(photo_id=photo_id, user_id=current_user_id)

    if int(check_permission['status_code']) != 200:

        return JsonResponse(check_permission)

    album_id = check_permission['album_id']
    request_data = request.POST

    # Update photo
    if request.method == 'PUT':

        response = update_photo(request_data=request_data, photo_id=photo_id)

    # Delete photo
    elif request.method == 'DELETE':

        response = delete_photo(photo_id=photo_id, album_id=album_id, user_id=current_user_id)

    else:

        response = {
            'status_code': 400,
            'status_message': 'Bad request'
        }

    return JsonResponse(response)


# Check if the user has the right to access the album
def check_album_permission(album_id='', user_id=''):

    album = session.query(Album).filter_by(id=album_id, user_id=user_id).first()

    # Get album
    if album:

        response = {
            'status_code': 404,
            'status_message': 'Not Found'
        }
        return response

    response = {
        'status_code': 200,
        'status_message': 'OK'
    }

    return response


# Check if the user has the right to access the photo
def check_photo_permission(photo_id='', user_id=''):

    photo = session.query(Photo).filter_by(id=photo_id).first()

    # Check if the photo exists
    if not photo:

        response = {
            'status_code': 404,
            'status_message': 'Not Found'
        }

        return response

    # Get album id
    current_album_id = photo.album_id

    album = session.query(Album).filter_by(id=current_album_id, user_id=user_id).first()

    # Get related album and user
    if not album:

        response = {
            'status_code': 404,
            'status_message': 'Not Found'
        }

        return response

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'album_id': str(current_album_id)
    }

    return response