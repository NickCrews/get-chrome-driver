import os
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from urllib.parse import urlparse


def download(url, output_path):
    """
    Download a file from url
    If output_path is None, the file will be downloaded directly in the current directory
    """

    try:
        session = __retry_session(retries=3,
                                  backoff_factor=0.1,
                                  status_forcelist=[429, 500, 502, 503, 504],
                                  method_whitelist=['GET'])
    except (HTTPError, ConnectionError, Timeout, RequestException) as err:
        raise err
    else:
        try:
            res = session.get(url=url)
            if res.status_code != 200:
                raise HTTPError('Invalid URL')

            file_name = __get_file_name_from_url(url)

            if output_path:
                __create_dir(output_path)
                output_path_with_file_name = output_path + '/' + file_name
            else:
                output_path_with_file_name = file_name

            with open(output_path_with_file_name, 'wb') as file:
                for chunk in res.iter_content(chunk_size=1048576):
                    if chunk:
                        file.write(chunk)

            return output_path_with_file_name, file_name
        except EnvironmentError as err:
            raise err
        finally:
            session.close()


def __retry_session(retries, backoff_factor, status_forcelist, method_whitelist):
    """ Retry session """

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=method_whitelist)

    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def __get_file_name_from_url(url):
    """ Get file name from url """

    path = urlparse(url).path
    return path.split('/')[-1]


def __create_dir(directory):
    """ Create a directory """

    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as err:
        raise err
