from base64 import b64encode
from hashlib import sha512
from jinja2 import contextfilter
from os import stat
from os.path import join


INTEGRITY_CACHE = {}


def discover_subresource_integrity(resource_path):
    return ''


@contextfilter
def generate_subresource_integrity(context, resource_path):
    global INTEGRITY_CACHE

    output_path = context['output_path']
    resource_path = join(output_path, resource_path)
    resource_hash, resource_time = INTEGRITY_CACHE.get(resource_path, (None, 0))
    resource_stat = stat(resource_path)

    if max(resource_stat.st_ctime_ns, resource_stat.st_mtime_ns) > resource_time:
        resource_hash = None

    if not resource_hash:
        with open(resource_path, 'rb') as resource_file:
            sha = sha512()
            sha.update(resource_file.read())
            resource_hash = f'sha512-{b64encode(sha.digest()).decode("ascii")}'

        INTEGRITY_CACHE[resource_path] = resource_hash, max(resource_stat.st_ctime_ns, resource_stat.st_mtime_ns)

    return resource_hash
