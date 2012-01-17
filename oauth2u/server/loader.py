import os

def load_from_directories(*directory_list):
    '''
    Executes all .py files from each directory. This function is used
    to load plugins and handlers in runtime

    '''
    for directory in directory_list:
        for filename in os.listdir(directory):
            if not filename.endswith('.py'):
                continue
            execfile(os.path.join(directory, filename), globals(), locals())
