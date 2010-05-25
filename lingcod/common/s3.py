"""
Lingcod's custom S3 wrapper
Provides some useful shortcuts to working with commom AWS S3 tasks
"""
from mimetypes import guess_type
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings


def s3_bucket(bucket=None):
    """
    Shortcut to a boto s3 bucket
    Uses settings.ACCESS_KEY, settings.AWS_SECRET_KEY
    defaults to settings.AWS_MEDIA_BUCKET
    """
    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_PASS_KEY)
    if not bucket:
        try: 
            bucket = settings.AWS_MEDIA_BUCKET
        except:
            raise Exception("No bucket specified and no settings.AWS_MEDIA_BUCKET")

    return conn.create_bucket(bucket)
    

def get_s3_url(key):
    """
    Uses the MEDIA_URL to guess the url for an S3 key
    """
    return ''.join(settings.MEDIA_URL, k.key)

def upload_to_s3(local_path, keyname, bucket=None, acl='public-read'):
    """
    Given a local filepath, bucket name and keyname (the new s3 filename), 
    this function will connect, guess the mimetype of the file, upload the contents and set the acl.
    Defaults to public-read
    """
    b = s3_bucket(bucket)
 
    content = open(local_path).read()
    mime = guess_type(local_path)[0]
    if not mime:
        mime = "text/plain"

    k = Key(b)
    k.key = keyname
    k.set_metadata("Content-Type", mime)
    k.set_contents_from_string(content)
    k.set_acl(acl)
    
    return get_s3_url(k)
