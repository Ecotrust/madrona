"""
Lingcod's custom S3 wrapper
Provides some useful shortcuts to working with commom AWS S3 tasks
"""
from mimetypes import guess_type
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings
import os

def s3_bucket(bucket=None):
    """
    Shortcut to a boto s3 bucket
    Uses settings.ACCESS_KEY, settings.AWS_SECRET_KEY
    defaults to settings.AWS_MEDIA_BUCKET
    """
    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    if not bucket:
        try: 
            bucket = settings.AWS_MEDIA_BUCKET
        except:
            raise Exception("No bucket specified and no settings.AWS_MEDIA_BUCKET")

    return conn.create_bucket(bucket)
    

def get_s3_url(b,k):
    """
    Returns the standard s3 url
    """
    return 'http://%s.s3.amazonaws.com/%s' % (b.name, k.key)

def upload_to_s3(local_path, keyname, mimetype=None, bucket=None, acl='public-read'):
    """
    Given a local filepath, bucket name and keyname (the new s3 filename), 
    this function will connect, guess the mimetype of the file, upload the contents and set the acl.
    Defaults to public-read
    """
    b = s3_bucket(bucket)
 
    if not os.path.exists(local_path):
        raise Exception("%s does not exist; can't upload to S3" % local_path)

    if not mimetype:
        mimetype = guess_type(local_path)[0]
        if not mimetype:
            mimetype = "text/plain"

    k = Key(b)
    k.key = keyname
    k.set_metadata("Content-Type", mimetype)
    k.set_contents_from_filename(local_path)
    k.set_acl(acl)
    
    return get_s3_url(b,k)

