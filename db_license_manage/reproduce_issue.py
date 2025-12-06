
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# User's Private Key
PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCiOkwQJ8422Ors
3+0qHguvUBjYIWDlIoFbqxNFVXCB8dxrQlWiFwEFyG+dAsMF6BQ2vtxE/9xqK5YX
+oUSsDz02K+LFy5d5qs9QjZk8RZ+Ewg3n42EaWAeFArT8dIm59np0x9RhTzEP2BW
tSjtooeQyaB2AWny6Cr7KaUbtlyU9hKXKddX3lvIuU8g+lqU3ODy3VYztuAYpx1N
5J/CiFezYvOr4z7qP7+UyfdAgxMftccAJGDwV84k3YWBAxL/kffDetfGqsHZQ6Q7
VEVk4Psmz+ggpTph0z6/GO3vrzMtIlsBCpRFIo9aSboUjpn74mpZ8tMYk4oRjgW4
bf6B9Ki/AgMBAAECggEAAd18uWTTxKKq1M1gSy8sQDhCCN4dYJUMerLVVmM8l2nh
+GO7W1E7ZEchLWN2PY+lB9oa6zor3RaiM6VgOU5IbSI+pnE+SbsYtewYdwGkmg96
9TTC6kZR4hal5zjtCyB4S21vez72a2U1JNoRXeYT+/CthR3QC4hq0hdw/AgVOWs0
KpBKDwsVcGRt3UKODAXOhNFW2m3rRKuKpF8RwHIWqibfyGKy0aiBBeM6us4x96tM
KzdepMDhrHWAcjLm+RVuscbOHwb62+flu6U9XfApZyl4XSGUPJTjYRjS5m4ZoK3y
GZq4JcWUfzEvIFig2NE3pT6D7HIY7mR1as+X/lrbkQKBgQC/j7cdCorQqVj6QK6w
4lx/dvg1LSek2MxKLxmD+UnylzqnF5KAqMzSpa//Fl3PPJuaZc0Q2mCG8qydRGrd
0wLqxZF6fUsfrvLp8yYYUckXPRBmGvIT9NDcw/b4Ec2/qgqZ+V7gwh80UZbS6f6A
S1e1P9PSPpk5KaXU9tWBL/YrDwKBgQDYzIRaYVKzOI/6m90j+urgrWBmPi+GeSq6
sCI2SAYhFCkAN72QGT+7Xhz8vUgqnzuGSqg4bnYy3YjDpUnWY6FNeRH/vjZkijT9
tRQuX4bfN2xuSE9PJBdKX6EG8A6eOa6tTr1IUwgFUzZG9wErtvml05GceB+PbEa0
fJ+FUmJnUQKBgQCcVAFgrtjIHluhpqWpbqGD2CgI5XfD3LUjGTrea9OAKRBRijgh
zR+SDGsLZkpaNCDcKJXoWf6KQoLBuTLpIinwRBlL9/IVwiU07Rw6novX7hpy6SyD
QrgsYbQrkAPzlSYfr9VQ4LqsbKUELLdoJZRHMvZ/TlymvKk7mdB1JBnl2wKBgQCU
SGYqTzC6ZnCL73l0t5VY8RzjMZtd9ZgVMo1j5SVUEK7ueDGO0sY1iGx5LZmjlV+o
PX4LgvoTVlTJxE7ZdTGJhMqbymT3pVQTR3wzL6FXIVhnoculDMFlXD0OOrk03a0s
2pM6WZg91ClmpmFFnhPoqOmKRNsJRPyjTC3riWrG0QKBgEvmYpGBB5D+AA783Uat
AC2qCIXsyx0nXgyGvk1L/M2Hiq9ccIiv4DJxOEkEZ/J8sG2QY6ZH+4xaDPUDiXDe
vnLSu7WhEdyQdXT+8mGsnK6NlyBDKXFmp6Z/SWxdQBWiJs/yzTrRV5rOiVUcGD+W
dvunsMhkNSrcZp/jDieT0rGu
-----END PRIVATE KEY-----"""

# User's Token
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJESUdJVEFMVUIiLCJzdWIiOiJDbGllbnRlIEV4ZW1wbG8gTGRhIiwidXVpZCI6ImU2OWFhNTk4LWE0MzgtMTFmMC05NGY1LTVkMjc5ZThmYjRjMyIsImV4cCI6MTc2NDg4MjI5NSwiaWF0IjoxNzY0NDUwMjk1fQ.Ed1MKljOsUzAJCa5Hm91s2U2IH0x2qmHTvch_YsAdwEdWjrBrI4aJ5qRxYb_QIiduu3HlcZnDKeAh2ZKyje9XCskur_Gdm1DG1AgMwSVygQ0cNvJ6AztMiNLHc0QBYrRnlTk0h48E4iM8-sgIOVAPlevKsVy3AvHSFbi1KtDwSDY8tZAk6Qy-WUDw84iEzWhm7NYbcWcZA8SIrwTe6TwCkR-4OO1Y5yxlSJFCgmPrc4X9j5wVlVbt4eVfjnNfJNzsrHawahE2oylLgj0LFL1d_KHixLIg6f0fYi5SBa1cqgG-9_vkIlHiYL3c4I9mZ8f8SfiRRQ0YgkTihdqo1em1w"

def get_public_key_pem(private_key_pem):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode('utf-8')

try:
    print("--- Generating Public Key from Private Key ---")
    public_key_pem = get_public_key_pem(PRIVATE_KEY_PEM)
    print(public_key_pem)
    print("--------------------------------------------")

    print("\n--- Attempting to Decode Token with Generated Public Key ---")
    decoded = jwt.decode(TOKEN, public_key_pem, algorithms=["RS256"])
    print("SUCCESS: Token decoded successfully.")
    print("Payload:", decoded)

except Exception as e:
    print(f"ERROR: {e}")
