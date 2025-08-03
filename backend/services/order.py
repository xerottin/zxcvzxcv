import random
import string


def generate_order_id() -> str:
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"order#{suffix}"