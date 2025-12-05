
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# 1. Generate a valid key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Serialize to PEM (multi-line)
pem_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

print(f"Original PEM:\n{pem_public}")

# 2. Simulate single-line (browser input behavior)
# Replace newlines with spaces
single_line_pem = pem_public.replace('\n', ' ')
print(f"\nSingle Line PEM:\n{single_line_pem}")

# 3. Create a token
payload = {'some': 'data'}
token = jwt.encode(payload, private_key, algorithm='RS256')

# 4. Try to decode with single-line key
try:
    decoded = jwt.decode(token, single_line_pem, algorithms=['RS256'])
    print("\nSUCCESS: Decoded with single-line key!")
except Exception as e:
    print(f"\nFAILURE: Could not decode with single-line key. Error: {e}")

# 5. Try to decode with reconstructed key
try:
    # Simple reconstruction logic
    reconstructed = single_line_pem.replace('-----BEGIN PUBLIC KEY----- ', '-----BEGIN PUBLIC KEY-----\n')
    reconstructed = reconstructed.replace(' -----END PUBLIC KEY-----', '\n-----END PUBLIC KEY-----')
    # The middle part might still have spaces instead of newlines, let's see if that matters
    # Actually, base64 ignores spaces, so it might work if headers are on own lines.
    
    decoded = jwt.decode(token, reconstructed, algorithms=['RS256'])
    print("\nSUCCESS: Decoded with reconstructed key!")
except Exception as e:
    print(f"\nFAILURE: Could not decode with reconstructed key. Error: {e}")
