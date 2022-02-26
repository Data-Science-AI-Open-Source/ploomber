import os
from glob import glob
import zipfile
from pathlib import Path

import click
import requests

HOST = 'https://lawqhyo5gl.execute-api.us-east-1.amazonaws.com/api/'


def _get_api_key():
    API_KEY = os.environ.get('PLOOMBER_CLOUD_KEY')

    if not API_KEY:
        raise ValueError('missing api key')

    return API_KEY


def zip_project():
    if Path('project.zip').exists():
        click.secho('Deleting existing project.zip...', fg='yellow')
        Path('project.zip').unlink()

    files = glob('**/*', recursive=True)

    # TODO: ignore __pycache__, ignore .git directory
    with zipfile.ZipFile('project.zip', 'w', zipfile.ZIP_DEFLATED) as zip:
        for path in files:
            zip.write(path, arcname=path)


def get_presigned_link():
    return requests.get(f'{HOST}/upload',
                        headers={
                            'Authorization': _get_api_key()
                        }).json()


def upload_zipped_project(response):
    object_name = 'project.zip'

    with open(object_name, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response['url'],
                                      data=response['fields'],
                                      files=files)

    if http_response.status_code != 204:
        raise ValueError(f'An error happened: {http_response}')

    click.secho('Uploaded project, starting execution...', fg='green')


def upload_project():
    click.echo('Zipping project...')
    zip_project()
    click.echo('Uploading project...')
    response = get_presigned_link()
    upload_zipped_project(response)
