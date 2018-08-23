import uuid
from django.http import JsonResponse
from .models import User, EyeColor, Country, session
from service.settings import ACCESS_TOKEN_EXPIRE_DURATION
from directory.views import get_eye_color, get_country
from datetime import datetime, timedelta
from sqlalchemy_utils import get_columns


# Get users data
def get_users_data():

    users_data = []

    for user in session.query(User).all():
        current_user = {}
        current_user['user_id'] = user.id
        current_user['user_name'] = user.user_name
        current_user['user_surname'] = user.user_surname
        current_user['user_middle_name'] = user.user_middle_name
        current_user['user_date_of_birth'] = user.user_date_of_birth

        eye_color_id = user.eye_color_id
        country_id = user.country_id

        eye_color = get_eye_color(eye_color_id)
        country = get_country(country_id)

        current_user['eye_color_id'] = eye_color_id
        current_user['eye_color'] = eye_color
        current_user['country_id'] = country
        current_user['country'] = country_id

        users_data.append(current_user)

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'data': users_data
    }

    return response


# Create user
def create_user(request_data):

    user_email = request_data.get('user_email')
    user_pass_hash = request_data.get('user_pass_hash')

    # Check user_email and user_pass_hash
    if not user_email or not user_pass_hash:

        response = {
            'status_code': 400,
            'status_message': 'Bad Request'
        }

        return response

    # Get existing user by email
    existing_user_by_email = session.query(User).filter_by(user_email=user_email).first()

    if existing_user_by_email:

        response = {
            'status_code': 403,
            'status_message': 'Forbidden'
        }

        return response

    # Create access token
    access_token = uuid.uuid4().hex

    # Set token expired date
    token_expired_date = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_DURATION)

    # Create new user
    user = User(user_email=user_email, user_pass_hash=user_pass_hash, access_token=access_token, token_expired_date=token_expired_date)

    try:
        session.add(user)
        session.commit()

        user_id = user.id

        response = {
            'status_code': 201,
            'status_message': 'Created',
            'user_id': user_id,
            'access_token': access_token,
            'token_expired_date': token_expired_date
        }

        return response

    except:

        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

        return response


def get_users(request):

    # Get users data
    if request.method == 'GET':

        response = get_users_data()

    # Create new user
    elif request.method == 'POST':

        request_data = request.POST
        response = create_user(request_data)

    else:

        response = {
            'status_code': 400,
            'status_message': 'Bad request'
        }

    return JsonResponse(response)


# Get user data
def get_self_data(user_id=''):

    user = session.query(User).filter_by(id=user_id).first()

    user_name = user.user_name
    user_surname = user.user_surname
    user_middle_name = user.user_middle_name
    user_date_of_birth = user.user_date_of_birth
    user_email = user.user_email

    eye_color_id = user.eye_color_id
    country_id = user.country_id

    eye_color = get_eye_color(eye_color_id)
    country = get_country(country_id)

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'data': {
            'user_name': user_name,
            'user_surname': user_surname,
            'user_middle_name': user_middle_name,
            'user_date_of_birth': user_date_of_birth,
            'user_email': user_email,
            'eye_color_id': eye_color_id,
            'eye_color': eye_color,
            'country': country,
            'country_id': country_id
        }
    }

    return response


# Update user
def update_user(request_data, user_id=''):

    if len(request_data) == 0:

        response = {
            'status_code': 400,
            'status_message': 'Bad request'
        }

        return response

    user = session.query(User).filter_by(id=user_id).first()

    # This columns can't be changed in this method
    deprecated_columns_to_change = ['id', 'user_pass_hash', 'access_token', 'token_expired_date']

    # Get columns names
    existing_columns = get_columns(user.__table__)
    existing_columns_names = list(map(lambda x: str(x).replace('users_.', ''), existing_columns))

    for key, value in request_data.items():
        if (key in existing_columns_names) and (key not in deprecated_columns_to_change) and value:

            if key == 'user_name':
                user.user_name = value

            if key == 'user_surname':
                user.user_surname = value

            if key == 'user_middle_name':
                user.user_middle_name = value

            if key == 'user_date_of_birth':

                if type(value) == int and datetime.fromtimestamp(value) < datetime.now():

                    user.user_date_of_birth = datetime.fromtimestamp(value)

                else:
                    print('user_date_of_birth is not correct', key, value)

            if key == 'eye_color_id':
                if len(value) == 36:
                    eye_color = session.query(EyeColor).filter_by(id=value).first()

                    if eye_color:
                        user.eye_color_id = eye_color.id
                    else:
                        print('wrong eye_color_id', key, value)

                else:
                    print('wrong uuid eye_color_id', key, value)

            if key == 'country_id':
                if len(value) == 36:
                    country = session.query(Country).filter_by(id=value).first()

                    if country:
                        user.country_id = country.id
                    else:
                        print('wrong country_id', key, value)
                else:
                    print('wrong uuid country_id', key, value)
        else:
            print('wrong key', key, value)

    try:
        session.commit()

        response = {
            'status_code': 200,
            'status_message': 'OK',
            'user_id': user_id
        }

        return JsonResponse(response)

    except:

        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

        return JsonResponse(response)


def get_user(request):
    access_token = request.GET.get('access_token', '')

    # Check access token
    check_token = check_access_token(access_token=access_token)

    if int(check_token['status_code']) != 200:
        # Return error
        return JsonResponse(check_token)

    user_id = check_token['user_id']

    # Get user data
    if request.method == 'GET':

        response = get_self_data(user_id=user_id)

    # Update user
    elif request.method == 'PUT':

        request_data = request.POST
        response = update_user(request_data=request_data, user_id=user_id)

    else:

        response = {
            'status_code': 400,
            'status_message': 'Bad request'
        }

    return JsonResponse(response)


def check_access_token(access_token=''):

    # Get user by access_token
    user = session.query(User).filter_by(access_token=access_token).first()
    if not user:

        response = {
            'status_code': 404,
            'status_message': 'Not Found'
        }

        return response

    current_date = datetime.now()

    token_expired_date = user.token_expired_date

    # Check expired date
    if token_expired_date < current_date:

        response = {
            'status_code': 401,
            'status_message': 'Unauthorized'
        }

        return response

    user_id = str(user.id)

    response = {
        'status_code': 200,
        'status_message': 'OK',
        'user_id': user_id
    }

    return response


def authorize_user(request):

    user_email = request.POST.get('user_email', '')
    user_pass_hash = request.POST.get('user_pass_hash', '')

    # Get user by email and hashed pass
    user = session.query(User).filter_by(user_email=user_email, user_pass_hash=user_pass_hash).first()

    if not user:

        response = {
            'status_code': 404,
            'status_message': 'Not Found'
        }

        return JsonResponse(response)

    # Get user id
    user = session.query(User).filter_by(user_email=user_email).first()
    user_id = user.id
    print(user_id)

    # Create access token
    access_token = uuid.uuid4().hex

    # Set token expired date
    token_expired_date = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_DURATION)

    # Update access token and token expired date
    user.access_token = access_token
    user.token_expired_date = token_expired_date

    try:
        session.commit()

        response = {
            'status_code': 200,
            'status_message': 'OK',
            'user_id': user_id,
            'access_token': access_token,
            'token_expired_date': token_expired_date
        }

        return JsonResponse(response)

    except:

        response = {
            'status_code': 500,
            'status_message': 'Internal Server Error'
        }

        return JsonResponse(response)