from __future__ import absolute_import, unicode_literals
from django.core.mail import EmailMessage
from smtplib import SMTPException
from service.celery import app
import os
import io
import base64
from PIL import Image


@app.task()
def save_photo(image_data='', photo_id='', user_id='', album_id='', email=''):

    data = ''
    if 'data:' in image_data and ';base64,' in image_data:
        content_type, data = image_data.split(';base64,')

    try:
        decoded_file = base64.b64decode(data)
    except TypeError:

        print('TypeError on create photo')
        return ''

    if content_type == 'data:image/jpeg':

        file_extension = 'jpg'

    elif content_type == 'data:image/png':

        file_extension = 'png'

    file_name_original = "%s.%s" % (photo_id, file_extension)
    file_name_middle = "%s_600x600.%s" % (photo_id, file_extension)
    file_name_thumb = "%s_150x150.%s" % (photo_id, file_extension)

    path = "./media/%s/%s" % (user_id, album_id)

    complete_path_original = "%s/%s" % (path, file_name_original)
    complete_path_middle = "%s/%s" % (path, file_name_middle)
    complete_path_thumb = "%s/%s" % (path, file_name_thumb)

    image_string = io.BytesIO(decoded_file)
    image = Image.open(image_string)
    image.seek(0)

    # Create path for this photo (/media/user_id/album_id/)
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        # Save original photo (/media/user_id/album_id/photo_id.extension)
        image.save(complete_path_original, image.format)

        # Save medium photo (/media/user_id/album_id/photo_id_600x600.extension)
        image.thumbnail((600, 600), Image.ANTIALIAS)
        image.save(complete_path_middle, image.format)

        # Save thumbnail photo (/media/user_id/album_id/photo_id_150x150.extension)
        image.thumbnail((150, 150), Image.ANTIALIAS)
        image.save(complete_path_thumb, image.format)

        return email

    except:

        return ''


@app.task()
def send_email(email=''):

    if not email:
        print('Email ERROR, no email')
        return 'ERROR'


    email_subject, email_body, email_from, email_to = 'Service message2', 'New photo has been uploaded', 'test@futbix.ru', email

    msg = EmailMessage(email_subject, email_body, email_from, [email_to])

    try:

        msg.send()
        print('Email OK', email)

        return 'OK'

    except SMTPException:

        print('Email ERROR', email)

        return 'ERROR'
