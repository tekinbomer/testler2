from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64

def generate_vapid_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_bytes = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint
    )

    public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip("=")
    private_key_b64 = base64.urlsafe_b64encode(private_key.private_numbers().private_value.to_bytes(32, 'big')).decode('utf-8').rstrip("=")

    return {
        "public": public_key_b64,
        "private": private_key_b64
    }

if __name__ == "__main__":
    keys = generate_vapid_keys()
    print("🔐 VAPID Public Key:\n", keys["public"])
    print("\n🗝️ VAPID Private Key:\n", keys["private"])
