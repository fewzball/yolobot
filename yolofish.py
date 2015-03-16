# -*- coding: utf-8 -*-
import ctypes


class YoloFish(object):
    def __init__(self, key):
        # libs/blowfish.so must exist in the root directory, i.e.
        # yolobot/libs/blowfish.so
        self.fish = ctypes.cdll.LoadLibrary('libs/blowfish.so')
        self.key = key

    def decrypt(self, cipher_text):
        """Decrypts a given string. Handles filling the buffer."""
        buffer_size = len(cipher_text) * 2 + 1
        c_memory_block = ctypes.create_string_buffer(buffer_size)
        self.fish.decrypt_string(
            ctypes.c_char_p(self.key),
            ctypes.c_char_p(cipher_text),
            c_memory_block,
            len(cipher_text)
        )
        c_memory_block[buffer_size - 1] = '\0'
        return ctypes.string_at(c_memory_block, buffer_size).strip('\x00')

    def encrypt(self, plaintext):
        """Encrypts a given string"""
        if len(plaintext) < 6:
            buffer_size = len(plaintext) * 2 + 1 + (12 - len(plaintext))
        else:
            buffer_size = len(plaintext) * 2 + 1 + (len(plaintext) % 12)
        c_memory_block = ctypes.create_string_buffer(buffer_size)
        self.fish.encrypt_string(
            ctypes.c_char_p(self.key),
            ctypes.c_char_p(plaintext),
            c_memory_block,
            len(plaintext)
        )
        c_memory_block[buffer_size - 1] = '\0'
        return '+OK {}'.format(ctypes.string_at(c_memory_block, buffer_size))
