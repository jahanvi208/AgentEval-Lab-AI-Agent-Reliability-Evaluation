"""Closed, deterministic tools: no eval, filesystem, network or side effects."""
import math

RECORDS = {
    'PRJ-101': {'owner': 'Mira', 'budget': 12000, 'spent': 8400, 'status': 'active'},
    'PRJ-102': {'owner': 'Kabir', 'budget': 9500, 'spent': 7600, 'status': 'blocked'},
    'PRJ-103': {'owner': 'Asha', 'budget': 18000, 'spent': 6300, 'status': 'active'},
    'PRJ-104': {'owner': 'Dev', 'budget': 6400, 'spent': 4800, 'status': 'complete'},
}
SCHEMAS = [
 {'name':'lookup', 'description':'Read a synthetic project record by exact project ID.', 'arguments':{'project_id':'string'}},
 {'name':'calculate', 'description':'Perform an arithmetic operation on two finite numbers. Divide is a/b.', 'arguments':{'operation':'add|subtract|multiply|divide','a':'number','b':'number'}},
]

class ToolError(ValueError):
    pass


def execute(name, arguments):
    if not isinstance(arguments, dict):
        raise ToolError('arguments must be an object')
    if name == 'lookup':
        if set(arguments) != {'project_id'} or not isinstance(arguments['project_id'], str):
            raise ToolError('lookup requires only string project_id')
        key = arguments['project_id']
        if key not in RECORDS:
            raise ToolError('project not found; do not invent a record')
        return dict(RECORDS[key])
    if name == 'calculate':
        if set(arguments) != {'operation', 'a', 'b'}:
            raise ToolError('calculate requires operation, a and b')
        op, a, b = arguments['operation'], arguments['a'], arguments['b']
        if any(type(v) not in (int, float) or not math.isfinite(v) or abs(v)>1e12 for v in (a,b)):
            raise ToolError('a and b must be finite numbers within +/-1e12')
        if op not in ('add','subtract','multiply','divide'):
            raise ToolError('unknown arithmetic operation')
        if op == 'divide' and b == 0:
            raise ToolError('division by zero; abstain')
        result = {'add':lambda:a+b,'subtract':lambda:a-b,'multiply':lambda:a*b,'divide':lambda:a/b}[op]()
        return result
    raise ToolError('unknown or prohibited tool')
