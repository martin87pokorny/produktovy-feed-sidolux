"""
Pomocný skript volaný z GH Action 'if: failure()' stepu.

Když workflow selže před tím, než stihne patchnout status do AT, ten zůstává
'Pending' nebo starý úspěšný stav. Tenhle skript pro všechny existující
záznamy v Feed_profile_index nastaví Status = Error a Posl. log = odkaz na
GH Actions run.

Skript je defensivní — pokud AT není dostupný, jen vytiskne chybu a skončí 0,
aby cleanup step ještě běžel. Selhání workflow je primárně signalizováno přes
GH Actions e-mail; AT update je bonus.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def _env(name: str) -> str | None:
    val = os.environ.get(name)
    return val.strip() if val else None


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')

    token = _env('AIRTABLE_TOKEN')
    base = _env('AIRTABLE_BASE_ID')
    table = 'Feed_profile_index'

    if not token or not base:
        print('AT credentials chybí — skip.')
        return 0

    server_url = _env('GITHUB_SERVER_URL') or 'https://github.com'
    repo = _env('GITHUB_REPOSITORY') or '?'
    run_id = _env('GITHUB_RUN_ID') or '?'
    run_url = f'{server_url}/{repo}/actions/runs/{run_id}'
    failed_step = _env('FAILED_STEP') or 'unknown'

    log_msg = (
        f'❌ Workflow selhal v kroku "{failed_step}" '
        f'({datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}). '
        f'Detaily: {run_url}'
    )

    # Stáhni všechny existující záznamy
    list_url = f'https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}'
    try:
        req = urllib.request.Request(list_url, headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f'AT list failed: {e}')
        return 0

    records = data.get('records', [])
    if not records:
        print(f'AT {table} prázdná — nic k aktualizaci.')
        return 0

    patches = [
        {'id': r['id'], 'fields': {
            'Status posl. běhu': 'Error',
            'Posl. log': log_msg,
        }} for r in records
    ]

    body = json.dumps({'records': patches}).encode()
    req = urllib.request.Request(
        list_url, data=body, method='PATCH',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            updated = len(json.loads(resp.read()).get('records', []))
        print(f'AT failure notification: {updated}/{len(patches)} profilů označeno Error.')
    except Exception as e:
        print(f'AT patch failed: {e}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
