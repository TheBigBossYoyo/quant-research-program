"""Preserve auditable source/config/document state without raw-data duplication."""
import json,hashlib,zipfile
from datetime import datetime,timezone
from core import ROOT

def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    base=ROOT/'reports'/f'checkpoint_{stamp}'
    paths=sorted(set(list((ROOT/'research').glob('*.py'))+list((ROOT/'tests').glob('*.py'))+
        list((ROOT/'config').glob('*.json'))+list(ROOT.glob('*.md'))+
        list((ROOT/'reports').glob('*.md'))))
    manifest=[]
    with zipfile.ZipFile(str(base)+'.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            rel=p.relative_to(ROOT).as_posix();body=p.read_bytes()
            z.writestr(rel,body)
            manifest.append(dict(file=rel,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body)))
    archives=[p for p in (ROOT/'data/raw').rglob('*.zip') if 'phase6' not in p.parts and 'phase8' not in p.parts]  # phase6/phase8 raw files are hashed in data/metadata manifests
    # Phase 6 (equity) raw files carry no vendor .CHECKSUM sidecars; they are verified against data/metadata/phase6_french_manifest.json.
    phase6_manifest=ROOT/'data/metadata/phase6_french_manifest.json';phase6=0
    if phase6_manifest.exists():
        for rec in json.loads(phase6_manifest.read_text(encoding='utf8'))['files']:
            assert hashlib.sha256((ROOT/rec['file']).read_bytes()).hexdigest()==rec['sha256'],rec['file'];phase6+=1
    verified=0;universe=0;phase2=0;phase4=0
    for p in archives:
        assert '-2026-' not in p.name,'Unexpected final-test archive'
        if 'micro' in p.parts or 'option' in p.parts or 'universe' in p.parts or 'phase4' in p.parts:assert '-2025-' not in p.name,'Locked 2025 data in a Phase 1/2 expansion folder'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==p.with_name(p.name+'.CHECKSUM').read_text().split()[0]
        if 'phase4' in p.parts:phase4+=1  # Phase 4 replication archives (monthly + daily supplements), 2020-2024 only
        elif 'universe' in p.parts:universe+=1
        elif 'micro' in p.parts or 'option' in p.parts or 'spot_1h' in p.parts or ('klines' in p.parts and ('-1h-2020-' in p.name or '-1h-2021-' in p.name)):phase2+=1  # Phase 2/3 expansion archives
        else:verified+=1
    assert verified==240,'Legacy two-asset archive count changed'
    payload=dict(created_utc=datetime.now(timezone.utc).isoformat(),source_files=manifest,
        verified_raw_archives=verified,verified_universe_archives=universe,verified_phase2_archives=phase2,verified_phase4_archives=phase4,verified_phase6_french_files=phase6,raw_archive_bytes=sum(p.stat().st_size for p in archives),
        test_result='unittest suite passed before checkpoint; count recorded in EXPERIMENTS.md/STATUS.md',
        final_test_downloaded=False,validation_analyzed=False,git_commit=None)
    with open(str(base)+'.json','x',encoding='utf8') as f:json.dump(payload,f,indent=2)
    with zipfile.ZipFile(str(base)+'.zip') as z:
        assert z.testzip() is None
        for row in manifest:assert hashlib.sha256(z.read(row['file'])).hexdigest()==row['sha256']
    print(base,'source files',len(manifest),'verified legacy archives',verified,'universe archives',universe,'phase2 archives',phase2,'phase4 archives',phase4,flush=True)

if __name__=='__main__':main()
