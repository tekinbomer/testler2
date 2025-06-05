from vapid import Vapid01

# mailto: eposta (zorunlu)
email = "mailto:siparis@tarotalemi.com"

# Anahtarları oluştur
vapid = Vapid01()
private_key, public_key = vapid.create_keys()
vapid.set_claims(sub=email)

print("🔐 VAPID Public Key:\n", public_key.decode())
print("\n🗝️ VAPID Private Key:\n", private_key.decode())
