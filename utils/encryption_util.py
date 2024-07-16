from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import binascii

class EncryptionUtil:
    UTF8 = 'utf-8'
    GBK = 'gbk'

    # 修改成对应秘钥!!!
    strDefaultKey = "wn8pjccU0I"
    charset = UTF8

    def __init__(self, key=None):
        if key is None:
            key = self.strDefaultKey
        self.key = self.get_key(key.encode(self.charset))
        self.encrypt_cipher = DES.new(self.key, DES.MODE_ECB)
        self.decrypt_cipher = DES.new(self.key, DES.MODE_ECB)

    @staticmethod
    def byte_arr_to_hex_str(byte_arr):
        return binascii.hexlify(byte_arr).decode()

    @staticmethod
    def hex_str_to_byte_arr(hex_str):
        return binascii.unhexlify(hex_str.encode())

    def encrypt(self, plaintext):
        plaintext_bytes = plaintext.encode(self.charset)
        padded_data = pad(plaintext_bytes, DES.block_size)
        encrypted_bytes = self.encrypt_cipher.encrypt(padded_data)
        return self.byte_arr_to_hex_str(encrypted_bytes)

    def decrypt(self, ciphertext):
        encrypted_bytes = self.hex_str_to_byte_arr(ciphertext)
        decrypted_bytes = self.decrypt_cipher.decrypt(encrypted_bytes)
        unpadded_data = unpad(decrypted_bytes, DES.block_size)
        return unpadded_data.decode(self.charset)

    @staticmethod
    def get_key(key_bytes):
        # 创建一个空的8位字节数组（默认值为0）
        arrB = bytearray(8)
        # 将原始字节数组转换为8位
        for i in range(min(len(key_bytes), len(arrB))):
            arrB[i] = key_bytes[i]

        # 生成密钥
        return bytes(arrB)

if __name__ == "__main__":
    # 需要加密的字符串
    str_to_encrypt = "17768102221"

    # 加密
    encryption_util = EncryptionUtil()
    encrypted_str = encryption_util.encrypt(str_to_encrypt)
    print("加密后结果  ->", encrypted_str)

    # 解密
    decrypted_str = encryption_util.decrypt(encrypted_str)
    print("解密后结果  ->", decrypted_str)
