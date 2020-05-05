from ovp.apps.donations.backends.zoop import ZoopBackend


def card_token(card_number):
    token = ZoopBackend().generate_card_token(
        holder_name="Test",
        expiration_month="03",
        expiration_year="2018",
        security_code="123",
        card_number=card_number)
    return token.json()["id"]
