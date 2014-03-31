from boto.s3.connection import S3Connection
from boto.s3.key import Key


class S3Interface(object):

    def __init__(self, access_key, secret_key, bucket_name):
        super(S3Interface, self).__init__()
        self._conn = S3Connection(access_key, secret_key)
        self._bucket = self._conn.get_bucket(bucket_name)

    def _construct_key(self, file_name):
        k = Key(self._bucket)
        k.key = file_name
        return k

    def write_string(self, string, file_name, content_type=None):
        k = self._construct_key(file_name)
        k.set_contents_from_string(string)
        k.set_acl('public-read')
        if content_type:
            k.set_metadata('Content-Type', content_type)
        # noinspection PyTypeChecker
        return k.generate_url(expires_in=0, query_auth=False)

    def read_string(self, file_name):
        k = self._construct_key(file_name)
        return k.get_contents_as_string()
