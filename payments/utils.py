import random
import string

def generate_secret_hash(length=32):
    # Создаем строку из букв (верхний и нижний регистр) и цифр
    characters = string.ascii_letters + string.digits
    # Генерируем случайную строку заданной длины
    secret_hash = ''.join(random.choice(characters) for i in range(length))
    return secret_hash