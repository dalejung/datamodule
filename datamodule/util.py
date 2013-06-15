from collections import OrderedDict
import ast

def _get_di_vars(code):
    """
    Running through an ast.Module and returning DATAMODULE variables. 
    These are just simple assignments with the name prefixed with
    DATAMODULE. 

    DATAMODULE_ENALBLED = True
    DATAMODULE_CACHE_KEY = 'some_key'
    """
    data = OrderedDict()
    for node in code.body:
        if isinstance(node, ast.Assign):
            try:
                names = [n.id for n in node.targets]
                value = ast.literal_eval(node.value)
            except:
                continue

            names = [name for name in names if name.startswith('DATAMODULE')]
            for name in names:
                data[name] = value
    return data
