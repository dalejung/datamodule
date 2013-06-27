import ast

def _get_assign_targets(nodes):
    """
    Parameters
    ----------
    nodes : list of ast.Node
        Usually the code.body of an ast.parse

    Return
    -------
    targets : list 
        List all the targets of assignment statements. Only goes one level
    """
    targets = []
    for node in nodes:
        if not isinstance(node, ast.Assign):
            return False
        for t in node.targets:
            try:
                name = t.id
                targets.append(name)
            except:
                continue
    return targets
