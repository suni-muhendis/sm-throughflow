"""Strict identity checks; no post-campaign executable or docstring changes."""
import hashlib
import json
import zipfile
from validation.campaign import ROOT
from sm_throughflow.provenance import runtime_identity

def verify(campaign):
    manifest=json.loads((campaign/'manifest.json').read_text())
    identity=runtime_identity()
    assert manifest['runtime']==identity
    assert hashlib.sha256((campaign/'source.zip').read_bytes()).hexdigest()==manifest['archive_sha256']
    names={p.relative_to(ROOT).as_posix() for p in (ROOT/'src').rglob('*.py')}
    archived={n for n in manifest['files'] if n.startswith('src/') and n.endswith('.py')}
    assert names==archived
    with zipfile.ZipFile(campaign/'source.zip') as archive:
        assert all(archive.read(n)==(ROOT/n).read_bytes() for n in names)
    return dict(campaign_source_sha256=identity['source_sha256'],current_source_sha256=identity['source_sha256'],
                all_package_files_byte_identical=True,runtime_identity_equal=True)
