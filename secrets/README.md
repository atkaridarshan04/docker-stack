# Secrets

Credentials are managed via Docker Secrets — mounted as read-only files inside containers at `/run/secrets/<name>`. They are never passed as environment variables or baked into images.

## Why Docker Secrets

Plain environment variables are visible in `docker inspect`, process listings, and crash dumps. Docker Secrets:

- Mount as read-only files — containers can read but not modify them
- Are only shared with services that explicitly declare them
- Never appear in `docker inspect` environment output
- Are excluded from version control via `.gitignore`

## Secrets in This Project

| Secret file | Used by | Purpose |
|-------------|---------|---------|
| `db_root_pw.txt` | MySQL | MySQL root password |
| `db_admin_pw.txt` | MySQL, Flask App, mysqld-exporter | Application DB user password |

## Setup

```bash
echo "your_secure_root_password" > secrets/db_root_pw.txt
echo "your_secure_admin_password" > secrets/db_admin_pw.txt
chmod 600 secrets/*.txt
```

## How Each Service Uses Secrets

**MySQL** — native `_FILE` suffix support:
```yaml
environment:
  MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_pw
  MYSQL_PASSWORD_FILE:      /run/secrets/db_admin_pw
```

**Flask App** — reads file at startup:
```python
with open(os.environ['MYSQL_PASSWORD_FILE']) as f:
    app.config['MYSQL_PASSWORD'] = f.read().strip()
```

**mysqld-exporter** — generates `.my.cnf` from secret at container start:
```sh
printf '[client]\nuser=admin\npassword=%s\n' "$(cat /run/secrets/db_admin_pw)" > /tmp/my.cnf
```

## Verification

After starting the stack, confirm secrets are not exposed as environment variables:

```bash
docker inspect flask-app | grep -A5 '"Env"'
# Should show MYSQL_PASSWORD_FILE=/run/secrets/db_admin_pw — not the actual password

docker inspect mysql | grep -A5 '"Env"'
# Should show MYSQL_ROOT_PASSWORD_FILE=/run/secrets/db_root_pw — not the actual password
```

## Security Notes

- `secrets/*.txt` is in `.gitignore` — never commit these files
- Set `chmod 600` on secret files to restrict host-level read access
- To rotate a password: update the secret file and run `docker compose up -d --force-recreate <service>`
