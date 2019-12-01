import os
import shutil


def write_file(app, request):
    # check file is passed
    if 'file' not in request.files:
        return {'verdict': 1, 'message': 'No file to write.'}
    file = request.files['file']

    # check the filepath or filename is passed
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0]

    try:
        path = os.path.join(app.config['root'], file_path)
        file.save(path)
        return {'verdict': 0, 'message': 'File was written.'}
    except:
        return {'verdict': 1, 'message': 'Wrong path for file write is given.'}


def init(app, request):
    root = app.config['root']
    try:
        shutil.rmtree(root)
        return {'verdict': 0, 'message': 'The file system was initialized.'}
    except:
        return {'verdict': 1, 'message': 'The file system was not initialized.'}


def create_file(app, request):
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0]

    try:
        path = os.path.join(app.config['root'], file_path)
        open(path).close()
        return {'verdict': 0, 'message': 'File was created.'}
    except:
        return {'verdict': 1, 'message': 'Wrong path for file creation is given.'}


def delete_file_or_dir(app, request):
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0]

    try:
        path = os.path.join(app.config['root'], file_path)

        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            os.removedirs(path)
        else:
            raise Exception
        return {'verdict': 0, 'message': 'File was created.'}
    except:
        return {'verdict': 1, 'message': 'Wrong path for file or directory deletion is given.'}


def copy_file(app, request):
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 2:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    from_path = json_data['arguments'][0]
    to_path = json_data['arguments'][1]

    try:
        from_path = os.path.join(app.config['root'], from_path)
        to_path = os.path.join(app.config['root'], to_path)
        shutil.copy2(from_path, to_path)
        return {'verdict': 0, 'message': 'File was created.'}
    except:
        return {'verdict': 1, 'message': 'Wrong paths for file copy are given.'}


def move_file(app, request):
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 2:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    from_path = json_data['arguments'][0]
    to_path = json_data['arguments'][1]

    try:
        from_path = os.path.join(app.config['root'], from_path)
        to_path = os.path.join(app.config['root'], to_path)
        shutil.move(from_path, to_path)
        return {'verdict': 0, 'message': 'File was created.'}
    except:
        return {'verdict': 1, 'message': 'Wrong paths for file move are given.'}


def read_file(app, request):
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0]

    try:
        path = os.path.join(app.config['root'], file_path)
        if os.path.isfile(path):
            with open(file_path) as file:
                msg = file.read()
            return {'verdict': 0, 'message': msg}
        else:
            raise Exception
    except:
        return {'verdict': 1, 'message': 'Wrong path for file read is given.'}


def read_dir(app, request):
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0]

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
    json_data = request.get_json()
    if 'arguments' not in json_data:
        return {'verdict': 1, 'message': 'No arguments for the command.'}
    elif len(json_data['arguments']) != 1:
        return {'verdict': 1, 'message': 'Wrong number of arguments is passed.'}
    file_path = json_data['arguments'][0]

    try:
        path = os.path.join(app.config['root'], file_path)
        if not os.path.exists(path):
            os.makedirs(path)
            return {'verdict': 0, 'message': "The directory was created."}
        else:
            raise Exception
    except:
        return {'verdict': 1, 'message': 'Wrong path for directory read is given.'}