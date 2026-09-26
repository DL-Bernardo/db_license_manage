#!/usr/bin/env python3
"""
Setup and configure DIGITALUB License Tools locally.
Run this script once to initialize RSA keys and the license generator.
"""
import os
import sys

HOME = os.path.expanduser("~")
TARGET_DIR = os.path.join(HOME, "license_tools")
os.makedirs(TARGET_DIR, exist_ok=True)

PRIV_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCg+pLfZs7VhigO
fMDi7/FYWBA4OpQhu89E2+l1XAiirltjdMDwRe/vCiNxO5FPmRJOwCQonbgm3r4/
AKZ0d28k364At7QOLujKr34+d81asi6WnnoMiG+4Bkns99THkuG1lAViBViUH68G
5PBEECi5CvN7lYun+ktM4gPP0W3attr7763x4SeEjqUcwBpgGG03JkYmTfIyF6Wn
nNxnj9y4tHR3/nGdPeM6BzD7f04dhLI/2UwXgY6rGU7Tw32miEQ3D+Ctd0ifVyl2
XQMC0RqexXncHoEuNrcbwtnnvdwezKucDMqtU7owp6oY1ZRTLlWoVAYt8oLGEZeU
HnSJ6vfFAgMBAAECggEAEZEel3342sDD3Mbc5rbv86fSh0xPL3o3BWjpKlszfws/
YlRSnLXJF+EXmor5UcIexxS9LWh+uNEsWiQ4RfPln1TAgIgLgFO6qCmsAWWh9YCF
yH59S6JU7LRU+2TVJb0/38iKKNb0AmANwdcYaBkKVJ0fEnCwl5FfB8IPT+2nCwum
fHQMGicfDQmIr+vVyJOH7/+HBqSOZGp5fMw9/sZek1xwrbCi3G1jNsedXfXi4j60
/hSdlFsm5RG8a19NhR9Xs158C5QCWzVom1oipDJ8fgoNaGPxkZTj6POZXoyEL5U8
cDxK0h1/blmnfN/UvZSOkVC552DqRLCoXIkIaH7CqQKBgQDOcwpFk9tdUxC44xmA
GGZlAvqh0ldj51+z3e7K0rtXzxqdIlTHmxXw61daCNtix9hfwyjt2CvPD1ssdRWi
56a87+zgiMXOJcUkUpfy0qGtczyBDYKn+fa/bWaW48jiE/9UNQye7qQjRJY+AN+4
0dm5htld+qiU0DqNCPcqY6NtKQKBgQDHnapMaa8WAuat04+41/Uqd8oQDFn1X/Do
TRzRdlHDiY1iB0AjJ+JtPaU64ITM/ACYFLwxXGbJfSsxxFbSXPxBjLv7/22jtBPW
vVCIC9krqdsEVdKJURWmDiYOVlE/u3tzG+lXH5BUW2XTITYGjWjmjdbbtMtQ2bLQ
efm3EvPtPQKBgG0u4ivR+p3spFdjo8TfIqghXzPd7mHjp/WUVgnmUTYrTcP0uCmo
l34GuPfg30Xqs0BSEn9XaDPlxy5H7d1t7fzWVsyZCSPxTcXb+IhvZRo6a7FE1+jG
hfzPewYqCb+nG84JEFetlhkg2OSJycgRE7jO3H6bZjTtu0mDiFRexbuhAoGAOF6a
t8dkbRfWoqHKxU0e66Y2Rn/ma3dzZXZZPAFop4pRhaw8fXEG7Qhqf4zlk6laVZgN
aPcKA744E265geBGUBB5CXmhMYhpzctaUYDfDAiEU94UfTiLn4ABWS0g9plwDBqG
s1azgE7rG0sWoZUPWYQWd6a/f45qg5reXMeaYJUCgYBJIhZ9+yoGGMbw4m/hABZR
nCQFw+qe/z7Mt+4bke+mmZLrSaPVYwfOIU9sYF+XAbGcP1RwkNMglEhE4Vq6An6S
8FPzhbl2XDhdwAnXc1YKiK0yqTjTmSFpQ3vZiCoPGlZwXcIjRbpXt7SAupLAlZFb
F0npg7IvuitUHuHjG1KY7g==
-----END PRIVATE KEY-----"""

PUB_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoPqS32bO1YYoDnzA4u/x
WFgQODqUIbvPRNvpdVwIoq5bY3TA8EXv7wojcTuRT5kSTsAkKJ24Jt6+PwCmdHdv
JN+uALe0Di7oyq9+PnfNWrIulp56DIhvuAZJ7PfUx5LhtZQFYgVYlB+vBuTwRBAo
uQrze5WLp/pLTOIDz9Ft2rba+++t8eEnhI6lHMAaYBhtNyZGJk3yMhelp5zcZ4/c
uLR0d/5xnT3jOgcw+39OHYSyP9lMF4GOqxlO08N9pohENw/grXdIn1cpdl0DAtEa
nsV53B6BLja3G8LZ573cHsyrnAzKrVO6MKeqGNWUUy5VqFQGLfKCxhGXlB50ier3
xQIDAQAB
-----END PUBLIC KEY-----"""

GEN_SCRIPT = """#!/usr/bin/env python3
import os, sys, argparse, datetime, jwt

KEY_DIR = os.path.dirname(os.path.abspath(__file__))
PRIV_PATH = os.path.join(KEY_DIR, "private_key.pem")

def create_token(client_name: str, db_uuid: str, days: int = 365):
    with open(PRIV_PATH, "r") as f:
        priv_key = f.read().strip()
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(days=days)
    payload = {
        'iss': 'DIGITALUB',
        'sub': client_name.strip(),
        'uuid': db_uuid.strip(),
        'exp': int(exp.timestamp()),
        'iat': int(now.timestamp())
    }
    return jwt.encode(payload, priv_key, algorithm="RS256"), now, exp

def main():
    parser = argparse.ArgumentParser(description="DIGITALUB License Token Generator")
    parser.add_argument("--client", "-c", help="Client name (e.g. 'KING PEDZIO')")
    parser.add_argument("--uuid", "-u", help="Database UUID")
    parser.add_argument("--days", "-d", type=int, default=365, help="Validity in days")
    args = parser.parse_args()

    client = args.client or input("Client Name: ").strip()
    uuid = args.uuid or input("Database UUID: ").strip()
    days = args.days

    token, start, exp = create_token(client, uuid, days)
    print("\\n" + "=" * 65)
    print(f"Client    : {client}")
    print(f"UUID      : {uuid}")
    print(f"Days      : {days} days")
    print(f"Expires   : {exp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("-" * 65)
    print("TOKEN (Copy into Odoo Settings -> Licensing -> License Token):")
    print("-" * 65)
    print(token)
    print("=" * 65 + "\\n")

if __name__ == "__main__":
    main()
"""

# Write files
priv_path = os.path.join(TARGET_DIR, "private_key.pem")
pub_path = os.path.join(TARGET_DIR, "public_key.pem")
gen_path = os.path.join(TARGET_DIR, "generate_license.py")

with open(priv_path, "w") as f:
    f.write(PRIV_KEY + "\n")
os.chmod(priv_path, 0o600)

with open(pub_path, "w") as f:
    f.write(PUB_KEY + "\n")
os.chmod(pub_path, 0o644)

with open(gen_path, "w") as f:
    f.write(GEN_SCRIPT)
os.chmod(gen_path, 0o755)

print("\n" + "=" * 65)
print("✅ DIGITALUB LICENSE TOOLS INITIALIZED SUCCESSFULLY!")
print("=" * 65)
print(f"Private Key : {priv_path} (Permission: 600)")
print(f"Public Key  : {pub_path}")
print(f"Generator   : {gen_path}")
print("-" * 65)
print("RSA PUBLIC KEY (Paste into Odoo Settings -> Licensing -> RSA Public Key):")
print("-" * 65)
print(PUB_KEY)
print("=" * 65 + "\n")
