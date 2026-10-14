"""Verify manuscript artifacts and static evidence; never run training/attacks.

Run with Python 3.12+ from the repository root after building both PDFs.
"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import re
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Reports/manuscript_phase4'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    with (ROOT / path).open(newline='') as stream:
        return list(csv.DictReader(stream))


def expand(path):
    return re.sub(r'\\input\{([^}]+)\}', lambda m: expand(ROOT / (m[1] + '.tex')),
                  path.read_text())


def document(name, keys):
    text = expand(ROOT / (name + '.tex'))
    labels = re.findall(r'\\label\{([^}]+)\}', text)
    assert len(labels) == len(set(labels)), (name, 'duplicate labels')
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text)
    assert set(refs) <= set(labels), (name, set(refs) - set(labels))
    cites = {k for group in re.findall(r'\\cite(?:\[[^]]*\])*\{([^}]+)\}', text)
             for k in group.split(',')}
    assert cites <= keys, (name, cites - keys)
    assert '\\nocite{*}' not in text
    bbl = (ROOT / 'build' / (name + '.bbl')).read_text()
    printed = set(re.findall(r'\\bibitem\{([^}]+)\}', bbl))
    assert cites == printed, (name, 'uncited/missing bibliography items', cites ^ printed)
    # pdfTeX may emit T1 font bytes in box diagnostics; error markers are ASCII.
    log = (ROOT / 'build' / (name + '.log')).read_text(encoding='latin-1')
    assert not re.search(r'undefined|multiply defined|Overfull|LaTeX Error|LaTeX Warning', log)
    assert 'Output written on' in log
    biblog = (ROOT / 'build' / (name + '.blg')).read_text(encoding='latin-1')
    assert not re.search(r'Warning--|error message|unknown function', biblog)
    pdf = ROOT / 'build' / (name + '.pdf')
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    extracted = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
    assert '??' not in extracted
    return {'pages': int(re.search(r'Pages:\s+(\d+)', info)[1]),
            'citations': len(cites), 'labels': len(labels), 'pdf_sha256': sha(pdf),
            'underfull_boxes': len(re.findall('Underfull', log)),
            'nonblocking_package_warnings': re.findall(r'Package .* Warning:.*', log)}


def main():
    baseline = json.loads((OUT / 'baseline.json').read_text())
    for path, expected in baseline['protected_sha256'].items():
        assert sha(ROOT / path) == expected, ('protected artifact changed', path)
    for item in json.loads((OUT / 'source-manifest.json').read_text()):
        assert sha(ROOT / item['path']) == item['sha256'], ('source damage', item['path'])
    bib = (ROOT / 'references.bib').read_text()
    keys = re.findall(r'@\w+\{([^,]+),', bib)
    assert len(keys) == len(set(keys)) == 32
    ledger = csv_rows('Reports/manuscript_phase4/citation_ledger.csv')
    assert {r['key'] for r in ledger} == set(keys)
    assert sum(r['added_phase4'] == 'True' for r in ledger) == 12
    for field in ['doi', 'title']:
        values = [re.sub(r'[^a-z0-9]', '', r[field].lower()) for r in ledger if r[field]]
        assert len(values) == len(set(values)), ('duplicate', field)
    docs = {name: document(name, set(keys)) for name in ['main', 'supplement']}
    assert docs['main']['citations'] == 32
    for row in csv_rows('data/timestamp_paired.csv'):
        b, c, both, neither = [int(row[k]) for k in ['pgd_only','temp_only','both','neither']]
        assert b+c+both+neither == 100
        assert math.isclose(float(row['pgd_asr_fraction']), (b+both)/100)
        assert math.isclose(float(row['temp_asr_fraction']), (c+both)/100)
        d = b+c
        p = min(1, 2*sum(math.comb(d,j) for j in range(min(b,c)+1))/2**d) if d else 1
        assert math.isclose(p, float(row['reported_exact_p']))
        assert math.isclose(p, float(row['recomputed_exact_p']))
    validation = [float(r['validation_accuracy_percent']) for r in csv_rows('data/qsnn_validation.csv')]
    assert math.isclose(statistics.mean(validation), 97.272)
    assert round(statistics.stdev(validation), 4) == .2119
    grid = csv_rows('data/controlled_four_models.csv')
    assert len(grid) == 8 and all(int(r['attack_denominator']) == 1000 for r in grid)
    for row in grid:
        for field in ['asr_Binf_1_percent', 'asr_B0_200_percent']:
            assert math.isclose(float(row[field])*10, round(float(row[field])*10))
    for row in csv_rows('Reports/manuscript_phase4/compute_accounting.csv'):
        if row['method'] != 'TEMP':
            continue
        n0, ng = int(row['initial']), int(row['children_per_generation'])
        assert n0+4*ng == int(row['actual_proposed_candidates'])
        assert math.ceil(n0/64)+4*math.ceil(ng/64) == int(row['inferred_search_model_calls'])
    # Independent static check of the actual upstream loss and baseline source identity.
    resolved = json.loads((OUT / 'resolved_b0_source.json').read_text())
    upstream = OUT / 'upstream/utils/attack.py'
    tree = ast.parse(upstream.read_text())
    l0 = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == resolved['class_name'])
    penalties = [x.value for x in ast.walk(l0) if isinstance(x, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'penalty_budget' for t in x.targets)]
    expression = next(x for x in penalties if isinstance(x, ast.BinOp) and isinstance(x.op, ast.Div))
    assert isinstance(expression.left, ast.BinOp) and expression.left.left.value == 5
    for entry in json.loads((OUT / 'upstream-source.json').read_text()):
        if entry['path'].startswith('models/'):
            local = ROOT / 'results/phase3/recovery/source/experiments/nmnist/reference_models' / Path(entry['path']).name
            assert sha(local) == entry['sha256']
    vectors = {}
    for name in ['fig01_overview','fig02_matched_evaluation','fig03_grid_comparison']:
        listing = subprocess.check_output(['pdfimages','-list',str(ROOT/'figures'/f'{name}.pdf')], text=True)
        assert len(listing.strip().splitlines()) == 2, (name, 'embedded raster')
        assert '<image' not in (ROOT/'figures'/f'{name}.svg').read_text()
        vectors[name] = {ext:sha(ROOT/'figures'/f'{name}.{ext}') for ext in ['pdf','svg','png']}
    review = csv_rows('Reports/manuscript_phase4/response_to_review.csv')
    assert {r['comment_id'] for r in review} == {f'R{i}' for i in range(1,9)} | {f'M{i}' for i in range(1,14)}
    status = json.loads((OUT/'execution_status.json').read_text())
    assert status['real_experiments_completed'] == 0 and not status['manuscript_phase4_complete']
    tests = (OUT/'unit-tests.log').read_text()
    assert re.search(r'Ran 34 tests',tests) and tests.rstrip().endswith('OK')
    assert not re.search(r'Warning|FAIL|ERROR',tests)
    local_artifacts = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
                       and '.git' not in p.parts and p.suffix.lower() in {'.pt','.pth','.ckpt','.npz','.npy','.parquet'}]
    assert not local_artifacts, ('data/checkpoints availability changed; update blockers',local_artifacts)
    result = dict(status='passed',documents=docs,bibliography_entries=32,new_references=12,
                  citation_duplicates=0,protected_files_verified=len(baseline['protected_sha256']),
                  historical_data_and_phase3_unchanged=True,paired_rows_checked=16,grid_cells_checked=16,
                  source_files_hashed=37,unit_tests=34,unit_test_failures=0,
                  software_tests_only=True,real_experiments_completed=0,
                  local_candidate_data_or_weight_artifacts=local_artifacts,vector_figures=vectors,
                  source_level_B0_penalty=5,historical_runtime_B0=None,
                  visual_review='Reports/manuscript_phase4/visual_review.md')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='vector_figures'},indent=2))


if __name__ == '__main__':
    main()
