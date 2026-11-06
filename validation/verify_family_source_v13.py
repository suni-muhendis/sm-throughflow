"""Audit the one documentation-only correction made after the v13 numerical run."""
import ast
import hashlib
import json
import zipfile

from validation.campaign import ROOT
from sm_throughflow.provenance import runtime_identity

PATH='src/sm_throughflow/correlations/blade_geometry.py'
BEFORE='''    or NACA meanline it follows the actual surface. NASA TP-1337's PHISS
    denotes front-segment camber to the transition, NOT this shock angle.
'''
AFTER='''    or NACA meanline it follows the actual surface. The individual NASA
    reports' PHISS uses their assumed shock position, which need not coincide
    with this geometric foot; it is not an independent shock measurement.
'''


class WithoutDocstrings(ast.NodeTransformer):
    def visit_Module(self,node):
        self.generic_visit(node)
        if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
            node.body=node.body[1:]
        return node
    visit_FunctionDef=visit_Module
    visit_AsyncFunctionDef=visit_Module
    visit_ClassDef=visit_Module


def verify(campaign):
    """No generic source relaxation: allow only the exact PHISS docstring correction."""
    m=json.loads((campaign/'manifest.json').read_text())
    current=runtime_identity()
    for key in ('python','platform','dependencies'):
        assert m['runtime'][key]==current[key],key
    assert hashlib.sha256((campaign/'source.zip').read_bytes()).hexdigest()==m['archive_sha256']
    changed=[]
    with zipfile.ZipFile(campaign/'source.zip') as archive:
        names=sorted(n for n in archive.namelist() if n.startswith('src/sm_throughflow/') and n.endswith('.py'))
        assert names==sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'src/sm_throughflow').rglob('*.py'))
        for name in names:
            previous=archive.read(name)
            present=(ROOT/name).read_bytes()
            if present==previous:continue
            assert name==PATH,'Executable source changed; rerun the campaign'
            old=previous.decode('utf-8').replace('\r\n','\n')
            new=present.decode('utf-8').replace('\r\n','\n')
            assert old.count(BEFORE)==1 and old.replace(BEFORE,AFTER)==new
            canonical=lambda s:ast.dump(WithoutDocstrings().visit(ast.parse(s)),include_attributes=False)
            assert canonical(old)==canonical(new)
            changed.append(dict(path=name,change='PHISS docstring correction only',executable_ast_identical=True,
                before_sha256=hashlib.sha256(previous).hexdigest(),after_sha256=hashlib.sha256(present).hexdigest()))
    return dict(campaign_source_sha256=m['runtime']['source_sha256'],current_source_sha256=current['source_sha256'],
                numerical_source_unchanged=True,changes=changed,results_retagged=False)
