from vapid import Vapid01

def generate_keys():
    email = "mailto:siparis@tarotalemi.com"
    vapid = Vapid01()
    private_key, public_key = vapid.create_keys()
    vapid.set_claims(sub=email)
    return {
        "public": public_key.decode(),
        "private": private_key.decode()
    }
