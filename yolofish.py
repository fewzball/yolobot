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

    def _encrypt(self, plaintext):
        text_length = len(plaintext)
        if text_length < 6:
            buffer_size = text_length * 2 + 1 + (12 - text_length)
        else:
            buffer_size = text_length * 2 + 1 + (text_length % 12)

        c_memory_block = ctypes.create_string_buffer(buffer_size)
        self.fish.encrypt_string(
            ctypes.c_char_p(self.key),
            ctypes.c_char_p(plaintext),
            c_memory_block,
            len(plaintext)
        )
        c_memory_block[buffer_size - 1] = '\0'
        return '+OK {}'.format(
            ctypes.string_at(c_memory_block, buffer_size)
        ).rstrip('\x00') + '\x00'

    def encrypt(self, plaintext):
        """Encrypts a given string"""
        if len(plaintext) > 300:
            parts = plaintext.split()
            pieced_msg, final_messages = [], []
            for chunk in parts:
                if len(' '.join(pieced_msg)) + len(chunk) < 300:
                    pieced_msg.append(chunk)
                else:
                    final_messages.append(self._encrypt(' '.join(pieced_msg)))
                    pieced_msg = [chunk]
            if pieced_msg:
                final_messages.append(self._encrypt(' '.join(pieced_msg)))
            return final_messages
        else:
            return self._encrypt(plaintext)
