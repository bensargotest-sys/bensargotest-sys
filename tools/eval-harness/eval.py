#!/usr/bin/env python3
"""
Eval Harness — Define evaluations BEFORE writing code, run during, report after.

Usage:
    python3 tools/eval-harness/eval.py define evals/my-eval.yaml
    python3 tools/eval-harness/eval.py run my-eval
    python3 tools/eval-harness/eval.py list
    python3 tools/eval-harness/eval.py history [--eval my-eval]
"""

import argparse
import json
import yaml
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

EVALS_DIR = Path("/data/.openclaw/workspace/evals")
RESULTS_DIR = Path("/data/.openclaw/workspace/data/eval-results")

def define(args):
    """Validate and register an eval definition"""
    eval_path = Path(args.path)
    if not eval_path.exists():
        print(f"File not found: {eval_path}")
        return

    with open(eval_path) as f:
        spec = yaml.safe_load(f)

    required = ["name", "checks"]
    for r in required:
        if r not in spec:
            print(f"Missing required field: {r}")
            return

    print(f"✅ Eval defined: {spec['name']}")
    print(f"   Checks: {len(spec['checks'])}")
    for i, check in enumerate(spec['checks'], 1):
        print(f"   {i}. {check.get('name', 'unnamed')} — {check.get('type', 'command')}")

def run_eval(args):
    """Run an eval by name"""
    # Find eval file
    eval_file = None
    for ext in ['.yaml', '.yml', '.json']:
        candidate = EVALS_DIR / f"{args.name}{ext}"
        if candidate.exists():
            eval_file = candidate
            break

    if not eval_file:
        print(f"Eval not found: {args.name}")
        print(f"Available: {[f.stem for f in EVALS_DIR.glob('*.*')]}")
        return

    with open(eval_file) as f:
        if eval_file.suffix in ['.yaml', '.yml']:
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)

    print(f"Running eval: {spec['name']}")
    print("=" * 50)

    results = []
    passed = 0
    failed = 0
    start_time = time.time()

    for check in spec.get('checks', []):
        name = check.get('name', 'unnamed')
        check_type = check.get('type', 'command')

        if check_type == 'command':
            cmd = check.get('command')
            expected_exit = check.get('expected_exit', 0)
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                ok = result.returncode == expected_exit

                # Check for expected output if specified
                if ok and 'expected_output' in check:
                    ok = check['expected_output'] in result.stdout

                results.append({"name": name, "passed": ok, "output": result.stdout[:200], "error": result.stderr[:200]})
                if ok:
                    passed += 1
                    print(f"  ✅ {name}")
                else:
                    failed += 1
                    print(f"  ❌ {name} (exit: {result.returncode}, expected: {expected_exit})")
                    if result.stderr:
                        print(f"     {result.stderr[:100]}")
            except subprocess.TimeoutExpired:
                failed += 1
                results.append({"name": name, "passed": False, "error": "timeout"})
                print(f"  ❌ {name} (TIMEOUT)")

        elif check_type == 'file_exists':
            path = Path(check.get('path', ''))
            ok = path.exists()
            results.append({"name": name, "passed": ok})
            if ok:
                passed += 1
                print(f"  ✅ {name}")
            else:
                failed += 1
                print(f"  ❌ {name} — {path} not found")

        elif check_type == 'file_contains':
            path = Path(check.get('path', ''))
            pattern = check.get('pattern', '')
            try:
                content = path.read_text()
                ok = pattern in content
            except Exception:
                ok = False
            results.append({"name": name, "passed": ok})
            if ok:
                passed += 1
                print(f"  ✅ {name}")
            else:
                failed += 1
                print(f"  ❌ {name} — pattern not found")

    duration = time.time() - start_time
    total = passed + failed

    print("=" * 50)
    print(f"Results: {passed}/{total} passed ({failed} failed) in {duration:.1f}s")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=timezone.utc).strftime('%Y%m%d-%H%M%S')
    result_file = RESULTS_DIR / f"{args.name}-{ts}.json"
    result_file.write_text(json.dumps({
        "eval": spec['name'],
        "ts": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "passed": passed,
        "failed": failed,
        "total": total,
        "duration_sec": round(duration, 1),
        "checks": results
    }, indent=2))
    print(f"Results saved: {result_file.name}")

def list_evals(args):
    """List available evals"""
    evals = list(EVALS_DIR.glob('*.yaml')) + list(EVALS_DIR.glob('*.yml')) + list(EVALS_DIR.glob('*.json'))
    if not evals:
        print("No evals defined yet. Create one in evals/")
        return
    print("Available evals:")
    for e in evals:
        print(f"  - {e.stem}")

def history(args):
    """Show eval run history"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pattern = f"{args.eval}-*.json" if args.eval else "*.json"
    files = sorted(RESULTS_DIR.glob(pattern))
    if not files:
        print("No eval history.")
        return

    print(f"{'TIMESTAMP':<22} {'EVAL':<20} {'RESULT':<12} {'DURATION'}")
    print("-" * 65)
    for f in files[-20:]:
        data = json.loads(f.read_text())
        status = f"✅ {data['passed']}/{data['total']}" if data['failed'] == 0 else f"❌ {data['passed']}/{data['total']}"
        print(f"{data['ts']:<22} {data['eval']:<20} {status:<12} {data['duration_sec']}s")

def main():
    parser = argparse.ArgumentParser(description='Eval Harness')
    sub = parser.add_subparsers(dest='command')

    p_def = sub.add_parser('define', help='Validate eval definition')
    p_def.add_argument('path')

    p_run = sub.add_parser('run', help='Run an eval')
    p_run.add_argument('name')

    sub.add_parser('list', help='List available evals')

    p_hist = sub.add_parser('history', help='Show run history')
    p_hist.add_argument('--eval')

    args = parser.parse_args()
    if args.command == 'define': define(args)
    elif args.command == 'run': run_eval(args)
    elif args.command == 'list': list_evals(args)
    elif args.command == 'history': history(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
