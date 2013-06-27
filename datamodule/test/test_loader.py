from unittest import TestCase
import sys
import types
import imp
import ast

import datamodule.loader as loader
import datamodule.ast_tools as ast_tools
reload(loader)

fullname = 'datamodule.test.fake_data'
path = ['/Users/datacaliber/Dropbox/Projects/trading/python/lib/datamodule/datamodule/test']

mname, path = loader._get_mname_path(fullname)
code = loader._load_code(fullname)
withs = []
for node in code.body:
    if not isinstance(node, ast.With):
        continue
    withs.append(node)

for node in withs:
    try:
        call = node.context_expr.func.id
    except:
        continue
    if call == 'local_only':
        print ast_tools._get_assign_targets(node.body)

w = withs[0]
