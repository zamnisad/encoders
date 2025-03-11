import unittest
from encoders_decoders.rle import *


class TestRLE(unittest.TestCase):
    def test_empty_data(self):
        data = b''
        encoded = RLE.rle_encode(data)
        decoded = RLE.rle_decode(encoded)
        self.assertEqual(data, decoded)

    def test_single_byte(self):
        data = b'\xAB'
        encoded = RLE.rle_encode(data)
        self.assertEqual(encoded, b'\x01\xAB')
        decoded = RLE.rle_decode(encoded)
        self.assertEqual(data, decoded)

    def test_long_sequence(self):
        data = b'\x00' * 300
        encoded = RLE.rle_encode(data)
        # Должно разбить на 255 и 45
        self.assertEqual(encoded, b'\xFF\x00\x2D\x00')
        decoded = RLE.rle_decode(encoded)
        self.assertEqual(data, decoded)

    def test_mixed_data(self):
        data = b'\x01\x01\x02\x03\x03\x03\x03'
        encoded = RLE.rle_encode(data)
        self.assertEqual(encoded, b'\x02\x01\x01\x02\x04\x03')
        decoded = RLE.rle_decode(encoded)
        self.assertEqual(data, decoded)

    def test_image_data(self):
        # Тест для BW изображения 100x100 (10000 пикселей)
        img_data = b'\x00\xFF' * 5000
        encoded = RLE.rle_encode(img_data)
        self.assertLess(len(encoded), len(img_data))
        decoded = RLE.rle_decode(encoded)
        self.assertEqual(img_data, decoded)