#
# QR Code generator library (Python)
#
# Copyright (c) Project Nayuki. (MIT License)
# https://www.nayuki.io/page/qr-code-generator-library
#
"""
Generates QR Code symbols from text strings.
"""

from __future__ import annotations
import collections
from typing import List, Sequence, Tuple


class QrCode:
    """A QR Code symbol, which is a type of two-dimension barcode."""
    
    MIN_VERSION = 1
    MAX_VERSION = 40
    
    _PENALTY_N1 = 3
    _PENALTY_N2 = 3
    _PENALTY_N3 = 40
    _PENALTY_N4 = 10
    
    _ECC_CODEWORDS_PER_BLOCK = [
        # Version: (note that index 0 is for padding, and is unused)
        # 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40
        [-1,  7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],  # Low
        [-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28],  # Medium
        [-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],  # Quartile
        [-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],  # High
    ]
    
    _NUM_ERROR_CORRECTION_BLOCKS = [
        [-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8,  9,  9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25],  # Low
        [-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49],  # Medium
        [-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68],  # Quartile
        [-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 72, 74, 77],  # High
    ]
    
    @staticmethod
    def encode_text(text: str, ecl: "QrCode.Ecc") -> "QrCode":
        """Encodes text to a QR Code symbol."""
        segs = QrSegment.make_segments(text)
        return QrCode.encode_segments(segs, ecl)
    
    @staticmethod
    def encode_segments(segs: Sequence["QrSegment"], ecl: "QrCode.Ecc",
            minversion: int = 1, maxversion: int = 40, mask: int = -1, boostecl: bool = True) -> "QrCode":
        
        # Find the minimal version number to use
        for version in range(minversion, maxversion + 1):
            datacapacitybits = QrCode._get_num_data_codewords(version, ecl) * 8
            datausedbits = QrSegment.get_total_bits(segs, version)
            if datausedbits is not None and datausedbits <= datacapacitybits:
                break
        else:
            raise ValueError("Data too long for QR Code")
        
        # Increase error correction level if possible
        if boostecl:
            for newecl in (QrCode.Ecc.MEDIUM, QrCode.Ecc.QUARTILE, QrCode.Ecc.HIGH):
                if datausedbits <= QrCode._get_num_data_codewords(version, newecl) * 8:
                    ecl = newecl
        
        # Concatenate all segments to create the data bit buffer
        bb = _BitBuffer()
        for seg in segs:
            bb.append_bits(seg.mode.mode_bits, 4)
            bb.append_bits(seg.numchars, seg.mode.num_char_count_bits(version))
            bb.extend(seg.bitdata)
        
        # Add terminator and pad up to a byte
        datacapacitybits = QrCode._get_num_data_codewords(version, ecl) * 8
        bb.append_bits(0, min(4, datacapacitybits - len(bb)))
        bb.append_bits(0, (8 - len(bb) % 8) % 8)
        
        # Pad with alternating bytes
        padbyte = 0xEC
        while len(bb) < datacapacitybits:
            bb.append_bits(padbyte, 8)
            padbyte ^= 0xEC ^ 0x11
        
        # Pack bits into bytes in big endian
        datacodewords = bytearray([0] * (len(bb) // 8))
        for i, bit in enumerate(bb):
            datacodewords[i >> 3] |= bit << (7 - (i & 7))
        
        # Create the QR Code object
        return QrCode(version, ecl, datacodewords, mask)

    def __init__(self, version: int, ecl: "QrCode.Ecc", datacodewords: bytes, mask: int):
        self.version = version
        self.size = version * 4 + 17
        self.error_correction_level = ecl
        
        self._modules = [[False] * self.size for _ in range(self.size)]
        self._is_function = [[False] * self.size for _ in range(self.size)]
        
        # Function patterns
        self._draw_function_patterns()
        allcodewords = self._add_ecc_and_interleave(datacodewords)
        self._draw_codewords(allcodewords)
        
        # Do masking
        if mask == -1:  # Automatically choose best mask
            minpenalty = 1 << 30
            bestmask = 0
            for m in range(8):
                self._apply_mask(m)
                self._draw_format_bits(m)
                penalty = self._get_penalty_score()
                if penalty < minpenalty:
                    minpenalty = penalty
                    bestmask = m
                self._apply_mask(m)  # Undoes the mask due to XOR
            mask = bestmask
        self.mask = mask
        self._apply_mask(mask)
        self._draw_format_bits(mask)

    def get_module(self, x: int, y: int) -> bool:
        """Returns the color of the module at (x, y): True for dark, False for light."""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self._modules[y][x]
        return False

    def _draw_function_patterns(self):
        # Draw horizontal and vertical timing patterns
        for i in range(self.size):
            self._set_function_module(6, i, i % 2 == 0)
            self._set_function_module(i, 6, i % 2 == 0)
        
        # Draw 3 finder patterns
        self._draw_finder_pattern(3, 3)
        self._draw_finder_pattern(self.size - 4, 3)
        self._draw_finder_pattern(3, self.size - 4)
        
        # Draw alignment patterns
        alignpatpos = self._get_alignment_pattern_positions()
        numalign = len(alignpatpos)
        for i in range(numalign):
            for j in range(numalign):
                # Don't draw on the three finder corners
                if not ((i == 0 and j == 0) or (i == 0 and j == numalign - 1) or (i == numalign - 1 and j == 0)):
                    self._draw_alignment_pattern(alignpatpos[i], alignpatpos[j])
        
        # Dummy format bits
        self._draw_format_bits(0)
        self._draw_version()

    def _draw_finder_pattern(self, x: int, y: int):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                dist = max(abs(dx), abs(dy))
                qx, qy = x + dx, y + dy
                if 0 <= qx < self.size and 0 <= qy < self.size:
                    self._set_function_module(qx, qy, dist != 2 and dist != 4)

    def _draw_alignment_pattern(self, x: int, y: int):
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                self._set_function_module(x + dx, y + dy, max(abs(dx), abs(dy)) != 1)

    def _set_function_module(self, x: int, y: int, isdark: bool):
        self._modules[y][x] = isdark
        self._is_function[y][x] = True

    def _draw_format_bits(self, mask: int):
        data = self.error_correction_level.format_bits << 3 | mask
        rem = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits = (data << 10 | rem) ^ 0x5412
        
        for i in range(0, 6):
            self._set_module(8, i, _get_bit(bits, i))
        self._set_module(8, 7, _get_bit(bits, 6))
        self._set_module(8, 8, _get_bit(bits, 7))
        self._set_module(7, 8, _get_bit(bits, 8))
        for i in range(9, 15):
            self._set_module(14 - i, 8, _get_bit(bits, i))
        
        for i in range(0, 8):
            self._set_module(self.size - 1 - i, 8, _get_bit(bits, i))
        for i in range(8, 15):
            self._set_module(8, self.size - 15 + i, _get_bit(bits, i))
        self._set_module(8, self.size - 8, True)

    def _draw_version(self):
        if self.version < 7:
            return
        rem = self.version
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        bits = self.version << 12 | rem
        for i in range(18):
            bit = _get_bit(bits, i)
            a = self.size - 11 + i % 3
            b = i // 3
            self._set_function_module(a, b, bit)
            self._set_function_module(b, a, bit)

    def _set_module(self, x: int, y: int, isdark: bool):
        self._modules[y][x] = isdark

    def _draw_codewords(self, data: bytes):
        i = 0
        right = self.size - 1
        while right > 0:
            if right == 6:
                right -= 1
            for vert in range(self.size):
                for j in range(2):
                    x = right - j
                    upward = ((right + 1) & 2) == 0
                    y = (self.size - 1 - vert) if upward else vert
                    if not self._is_function[y][x] and i < len(data) * 8:
                        self._modules[y][x] = _get_bit(data[i >> 3], 7 - (i & 7))
                        i += 1
            right -= 2

    def _apply_mask(self, mask: int):
        for y in range(self.size):
            for x in range(self.size):
                if self._is_function[y][x]:
                    continue
                invert: bool
                if mask == 0:  invert = (x + y) % 2 == 0
                elif mask == 1: invert = y % 2 == 0
                elif mask == 2: invert = x % 3 == 0
                elif mask == 3: invert = (x + y) % 3 == 0
                elif mask == 4: invert = (x // 3 + y // 2) % 2 == 0
                elif mask == 5: invert = (x * y) % 2 + (x * y) % 3 == 0
                elif mask == 6: invert = ((x * y) % 2 + (x * y) % 3) % 2 == 0
                elif mask == 7: invert = ((x + y) % 2 + (x * y) % 3) % 2 == 0
                else: raise ValueError()
                self._modules[y][x] ^= invert

    def _get_penalty_score(self) -> int:
        result = 0
        # Horizontal / vertical runs of 5+ same color
        for y in range(self.size):
            runcolor = False
            runx = 0
            for x in range(self.size):
                if x == 0:
                    runcolor = self._modules[y][x]
                    runx = 1
                elif self._modules[y][x] == runcolor:
                    runx += 1
                    if runx == 5:
                        result += self._PENALTY_N1
                    elif runx > 5:
                        result += 1
                else:
                    runcolor = self._modules[y][x]
                    runx = 1
        for x in range(self.size):
            runcolor = False
            runy = 0
            for y in range(self.size):
                if y == 0:
                    runcolor = self._modules[y][x]
                    runy = 1
                elif self._modules[y][x] == runcolor:
                    runy += 1
                    if runy == 5:
                        result += self._PENALTY_N1
                    elif runy > 5:
                        result += 1
                else:
                    runcolor = self._modules[y][x]
                    runy = 1
        # 2x2 blocks
        for y in range(self.size - 1):
            for x in range(self.size - 1):
                color = self._modules[y][x]
                if color == self._modules[y][x+1] == self._modules[y+1][x] == self._modules[y+1][x+1]:
                    result += self._PENALTY_N2
        # Finder-like patterns
        for y in range(self.size):
            bits = 0
            for x in range(self.size):
                bits = ((bits << 1) & 0x7FF) | (1 if self._modules[y][x] else 0)
                if x >= 10 and (bits == 0x05D or bits == 0x5D0):
                    result += self._PENALTY_N3
        for x in range(self.size):
            bits = 0
            for y in range(self.size):
                bits = ((bits << 1) & 0x7FF) | (1 if self._modules[y][x] else 0)
                if y >= 10 and (bits == 0x05D or bits == 0x5D0):
                    result += self._PENALTY_N3
        # Dark module balance
        dark = sum(sum(1 for cell in row if cell) for row in self._modules)
        total = self.size * self.size
        k = (abs(dark * 20 - total * 10) + total - 1) // total - 1
        result += k * self._PENALTY_N4
        return result

    def _get_alignment_pattern_positions(self) -> List[int]:
        if self.version == 1:
            return []
        num = self.version // 7 + 2
        step = (self.version * 8 + num * 3 + 5) // (num * 4 - 4) * 2
        result = [self.size - 7]
        for _ in range(num - 1):
            result.append(result[-1] - step)
        result[-1] = 6
        return list(reversed(result))

    @staticmethod
    def _get_num_data_codewords(version: int, ecl: "QrCode.Ecc") -> int:
        return QrCode._get_num_raw_data_modules(version) // 8 - \
            QrCode._ECC_CODEWORDS_PER_BLOCK[ecl.ordinal][version] * \
            QrCode._NUM_ERROR_CORRECTION_BLOCKS[ecl.ordinal][version]

    @staticmethod
    def _get_num_raw_data_modules(version: int) -> int:
        result = (16 * version + 128) * version + 64
        if version >= 2:
            numalign = version // 7 + 2
            result -= (25 * numalign - 10) * numalign - 55
            if version >= 7:
                result -= 36
        return result

    def _add_ecc_and_interleave(self, data: bytes) -> bytes:
        ver = self.version
        ecl = self.error_correction_level
        numblocks = QrCode._NUM_ERROR_CORRECTION_BLOCKS[ecl.ordinal][ver]
        blockecc_len = QrCode._ECC_CODEWORDS_PER_BLOCK[ecl.ordinal][ver]
        rawcodewords = QrCode._get_num_raw_data_modules(ver) // 8
        numshortblocks = numblocks - rawcodewords % numblocks
        shortblocklen = rawcodewords // numblocks
        
        blocks = []
        rs = _ReedSolomonGenerator(blockecc_len)
        k = 0
        for i in range(numblocks):
            blocklen = shortblocklen - blockecc_len + (0 if i < numshortblocks else 1)
            dat = bytearray(data[k : k + blocklen])
            k += blocklen
            ecc = rs.get_remainder(dat)
            if i < numshortblocks:
                dat.append(0)
            dat.extend(ecc)
            blocks.append(dat)
        
        result = bytearray()
        for i in range(shortblocklen + 1):
            for j in range(numblocks):
                if i != shortblocklen - blockecc_len or j >= numshortblocks:
                    result.append(blocks[j][i])
        return bytes(result)

    class Ecc:
        """The error correction level in a QR Code symbol."""
        LOW      = None  # type: QrCode.Ecc
        MEDIUM   = None  # type: QrCode.Ecc
        QUARTILE = None  # type: QrCode.Ecc
        HIGH     = None  # type: QrCode.Ecc
        
        def __init__(self, ordinal: int, fb: int):
            self.ordinal = ordinal
            self.format_bits = fb

QrCode.Ecc.LOW      = QrCode.Ecc(0, 1)
QrCode.Ecc.MEDIUM   = QrCode.Ecc(1, 0)
QrCode.Ecc.QUARTILE = QrCode.Ecc(2, 3)
QrCode.Ecc.HIGH     = QrCode.Ecc(3, 2)


class QrSegment:
    """A segment of character/binary/control data in a QR Code symbol."""
    
    @staticmethod
    def make_bytes(data: bytes) -> "QrSegment":
        bb = _BitBuffer()
        for b in data:
            bb.append_bits(b, 8)
        return QrSegment(QrSegment.Mode.BYTE, len(data), bb)

    @staticmethod
    def make_alphanumeric(text: str) -> "QrSegment":
        ALPHANUMERIC_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
        bb = _BitBuffer()
        accumdata = 0
        accumcount = 0
        for c in text:
            idx = ALPHANUMERIC_CHARSET.find(c)
            if idx == -1:
                raise ValueError("String cannot be encoded in alphanumeric mode")
            accumdata = accumdata * 45 + idx
            accumcount += 1
            if accumcount == 2:
                bb.append_bits(accumdata, 11)
                accumdata = 0
                accumcount = 0
        if accumcount == 1:
            bb.append_bits(accumdata, 6)
        return QrSegment(QrSegment.Mode.ALPHANUMERIC, len(text), bb)

    @staticmethod
    def make_segments(text: str) -> List["QrSegment"]:
        # Try alphanumeric or fallback to byte
        try:
            return [QrSegment.make_alphanumeric(text)]
        except ValueError:
            return [QrSegment.make_bytes(text.encode("utf-8"))]

    @staticmethod
    def get_total_bits(segs: Sequence["QrSegment"], version: int) -> int:
        result = 0
        for seg in segs:
            ccbits = seg.mode.num_char_count_bits(version)
            if seg.numchars >= (1 << ccbits):
                return None
            result += 4 + ccbits + len(seg.bitdata)
        return result

    def __init__(self, mode: "QrSegment.Mode", numchars: int, bitdata: "_BitBuffer"):
        self.mode = mode
        self.numchars = numchars
        self.bitdata = bitdata

    class Mode:
        NUMERIC      = None
        ALPHANUMERIC = None
        BYTE         = None
        KANJI        = None
        ECI          = None
        
        def __init__(self, modebits: int, *charcountbits: int):
            self.mode_bits = modebits
            self._num_char_count_bits = charcountbits
            
        def num_char_count_bits(self, ver: int) -> int:
            return self._num_char_count_bits[(ver + 7) // 17]

QrSegment.Mode.NUMERIC      = QrSegment.Mode(0x1, 10, 12, 14)
QrSegment.Mode.ALPHANUMERIC = QrSegment.Mode(0x2,  9, 11, 13)
QrSegment.Mode.BYTE         = QrSegment.Mode(0x4,  8, 16, 16)
QrSegment.Mode.KANJI        = QrSegment.Mode(0x8,  8, 10, 12)
QrSegment.Mode.ECI          = QrSegment.Mode(0x7,  0,  0,  0)


class _BitBuffer(list):
    def append_bits(self, val: int, length: int):
        for i in reversed(range(length)):
            self.append((val >> i) & 1)


class _ReedSolomonGenerator:
    def __init__(self, degree: int):
        self._coefficients = bytearray([0] * degree)
        self._coefficients[-1] = 1
        root = 1
        for _ in range(degree):
            for j in range(degree):
                self._coefficients[j] = self._multiply(self._coefficients[j], root)
                if j + 1 < degree:
                    self._coefficients[j] ^= self._coefficients[j + 1]
            root = self._multiply(root, 0x02)

    def get_remainder(self, data: bytes) -> bytes:
        result = bytearray([0] * len(self._coefficients))
        for b in data:
            factor = b ^ result.pop(0)
            result.append(0)
            for i, coef in enumerate(self._coefficients):
                result[i] ^= self._multiply(coef, factor)
        return bytes(result)

    @staticmethod
    def _multiply(x: int, y: int) -> int:
        z = 0
        for i in reversed(range(8)):
            z = (z << 1) ^ ((z >> 7) * 0x11D)
            z ^= ((y >> i) & 1) * x
        return z


def _get_bit(x: int, i: int) -> bool:
    return ((x >> i) & 1) != 0
