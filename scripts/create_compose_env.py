"""Generate isolated Docker secrets without changing DagsHub's existing .env."""
from pathlib import Path
import secrets
root = Path(__file__).resolve().parents[1]
output = root / '.env.compose'
if output.exists():
    print('Existing .env.compose retained; credentials unchanged.')
else:
    output.write_text(
        'POSTGRES_PASSWORD=' + secrets.token_hex(24) + '\n' +
        'FLASK_SECRET_KEY=' + secrets.token_hex(32) + '\n',
        encoding='utf-8',
    )
    print('Created private .env.compose with generated secrets.')
# Existing .gitignore in Step 1 does not protect this filename.
ign = root / '.gitignore'
data = ign.read_text(encoding='utf-8') if ign.exists() else ''
lines = set(x.strip() for x in data.splitlines())
addition = [name for name in ['.env.compose', 'instance/', 'mlflow.db', 'mlruns/'] if name not in lines]
if addition:
    with ign.open('a', encoding='utf-8') as f:
        f.write('\n' + '\n'.join(addition) + '\n')
    print('Extended .gitignore for local secrets and runtime data.')
if not (root / 'models' / 'champion.keras').is_file():
    raise SystemExit('Missing models/champion.keras. Use the model generated in Step 2.')
if not (root / 'webapp' / 'app.py').is_file():
    raise SystemExit('Missing webapp/app.py. Merge this package into the existing project.')
print('Project/model verified for Docker Compose.')
