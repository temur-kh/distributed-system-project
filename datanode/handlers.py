import os
import shutil
import requests


def write_file(app, request):
    # check the filepath or filename is passed
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 2:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0][1:]
    file_obj = json_data['arguments'][1]

    try:
        path = os.path.join(app.config['root'], file_path)
        with open(path, 'wb') as file:
            file.write(file_obj)
        return {'verdict': 0, 'message': 'File was written.'}
    except:
        return {'verdict': 1, 'message': 'Wrong path for file write is given.'}


def init(app, request):
    # init root directory and format
    root = app.config['root']
    try:
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
        return {'verdict': 0, 'message': 'The file system was initialized.'}
    except:
        return {'verdict': 1, 'message': 'The file system was not initialized.'}


def create_file(app, request):
    # create a file
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0][1:]
    path = os.path.join(app.config['root'], file_path)
    try:
        open(path, 'wb').close()
        return {'verdict': 0, 'message': 'File was created.'}
    except:
        return {'verdict': 1, 'message': f'Wrong path for file creation is given: {path}.'}


def delete_file_or_dir(app, request):
    # delete file or directory by path
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0][1:]

    try:
        path = os.path.join(app.config['root'], file_path)

        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            os.removedirs(path)
        else:
            raise Exception
        return {'verdict': 0, 'message': 'File/directory was deleted.'}
    except:
        return {'verdict': 1, 'message': 'Wrong path for file or directory deletion is given.'}


def copy_file(app, request):
    # copy one file to another path
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 2:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    from_path = json_data['arguments'][0][1:]
    to_path = json_data['arguments'][1][1:]

    try:
        from_path = os.path.join(app.config['root'], from_path)
        to_path = os.path.join(app.config['root'], to_path)
        shutil.copy2(from_path, to_path)
        return {'verdict': 0, 'message': 'File was copied.'}
    except:
        return {'verdict': 1, 'message': 'Wrong paths for file copy are given.'}


def move_file(app, request):
    # move one file to another path
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 2:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    from_path = json_data['arguments'][0][1:]
    to_path = json_data['arguments'][1][1:]

    try:
        from_path = os.path.join(app.config['root'], from_path)
        to_path = os.path.join(app.config['root'], to_path)
        shutil.move(from_path, to_path)
        return {'verdict': 0, 'message': 'File was moved.'}
    except:
        return {'verdict': 1, 'message': 'Wrong paths for file move are given.'}


def read_file(app, request):
    # read a file content
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0][1:]

    try:
        path = os.path.join(app.config['root'], file_path)
        print(path)
        if os.path.isfile(path):
            with open(path, 'r') as file:
                msg = file.read()
            return {'verdict': 0, 'message': msg}
        else:
            raise Exception
    except:
        return {'verdict': 1, 'message': 'Wrong path for file read is given.'}


def read_dir(app, request):
    # read what files exist in a directory
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0][1:]

    try:
        path = os.path.join(app.config['root'], file_path)
        if os.path.isdir(path):
            msg_list = os.listdir(path)
            return {'verdict': 0, 'message': msg_list}
        else:
            raise Exception
    except:
        return {'verdict': 1, 'message': 'Wrong path for directory read is given.'}


def make_dir(app, request):
    # create a directory
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0][1:]

    try:
        path = os.path.join(app.config['root'], file_path)
        if not os.path.exists(path):
            os.makedirs(path)
            return {'verdict': 0, 'message': "The directory was created."}
        else:
            raise Exception
    except:
        return {'verdict': 1, 'message': 'Wrong path for directory read is given.'}


def recursive_repl(directory, url):
    # make recursive replication of all files to another node
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            requests.post(url,
                          json={'command': 'write_file', 'arguments': [path]},
                          files={path: open(path, 'rb')})
        else:
            requests.get(url, json={'command': 'make_dir', 'arguments': [path]})
            recursive_repl(path, url)


def replicate(app, request):
    # run a replication activity
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    url = json_data['arguments'][0]
    root = app.config['root']
    recursive_repl(root, url)
    return {'verdict': 0, 'message': 'Replication completed.'}
