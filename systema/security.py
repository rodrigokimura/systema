from nanoid import generate

from .management import settings


def generate_id():
    return generate(settings.nanoid_alphabet, settings.nanoid_size)
