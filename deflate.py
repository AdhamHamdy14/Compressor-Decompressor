LENGTH_TABLE = {
    # length_key (base_length): (symbol, extra_bits)
    3:   (257, 0), 4:   (258, 0), 5:   (259, 0), 6:   (260, 0),
    7:   (261, 0), 8:   (262, 0), 9:   (263, 0), 10:  (264, 0),
    11:  (265, 1), 13:  (266, 1), 15:  (267, 1), 17:  (268, 1),
    19:  (269, 2), 23:  (270, 2), 27:  (271, 2), 31:  (272, 2),
    35:  (273, 3), 43:  (274, 3), 51:  (275, 3), 59:  (276, 3),
    67:  (277, 4), 83:  (278, 4), 99:  (279, 4), 115: (280, 4),
    131: (281, 5), 163: (282, 5), 195: (283, 5), 227: (284, 5),
    258: (285, 0),
}

DISTANCE_TABLE = {
    # distance_key (base_dist): (symbol, extra_bits)
    1:     (0, 0), 2:     (1, 0), 3:     (2, 0), 4:     (3, 0),
    5:     (4, 1), 7:     (5, 1), 9:     (6, 2), 13:    (7, 2),
    17:    (8, 3), 25:    (9, 3), 33:    (10, 4), 49:    (11, 4),
    65:    (12, 5), 97:    (13, 5), 129:   (14, 6), 193:   (15, 6),
    257:   (16, 7), 385:   (17, 7), 513:   (18, 8), 769:   (19, 8),
    1025:  (20, 9), 1537:  (21, 9), 2049:  (22, 10), 3073:  (23, 10),
    4097:  (24, 11), 6145:  (25, 11), 8193:  (26, 12), 12289: (27, 12),
    16385: (28, 13), 24577: (29, 13),
}


class BitReader:
    def __init__(self, file_path):
        # Open file in read-binary mode
        self.file = open(file_path, "rb")
        # Buffer to store bits read from the file
        self.buffer = 0
        # Number of available bits in the buffer
        self.bit_count = 0

    def read_bits(self, n):
        # Read more bytes if the buffer has fewer than 'n' bits
        while self.bit_count < n:
            new_byte = self.file.read(1)
            # Return None if End of File (EOF) is reached
            if not new_byte:
                return None

            # Add the new byte to the buffer (LSB order)
            self.buffer |= (ord(new_byte) << self.bit_count)
            self.bit_count += 8

        # Create a mask to extract 'n' bits
        mask = (1 << n) - 1
        value = self.buffer & mask

        # Remove the consumed bits from the buffer
        self.buffer >>= n
        self.bit_count -= n

        return value

    def close(self):
        # Close the file stream
        self.file.close()


class BitWriter:
    def __init__(self, file_path):
        # Open file in write-binary mode
        self.file = open(file_path, "wb")
        # Buffer to store bits before writing as bytes
        self.buffer = 0
        # Current number of bits in the buffer
        self.bit_count = 0

    def write_bits(self, value, n_bits):
        # Shift and add new bits to the buffer (LSB order)
        self.buffer |= (value << self.bit_count)
        self.bit_count += n_bits

        # Extract and write full bytes (8 bits) to the file
        while self.bit_count >= 8:
            byte_to_write = self.buffer & 0xFF
            self.file.write(bytes([byte_to_write]))

            # Remove the written byte from buffer
            self.buffer >>= 8
            self.bit_count -= 8

    def close(self):
        # Write any remaining bits as a final byte
        if self.bit_count > 0:
            self.file.write(bytes([self.buffer & 0xFF]))
        self.file.close()

# Usage Example:
# writer = BitWriter("compressed.bin")
# writer.write_bits(1, 2)  # Write value 1 using 2 bits
# writer.close()


def get_length_symbol_and_extra(length: int) -> tuple:
    l_keys = sorted(LENGTH_TABLE.keys(), reverse=True)
    for k in l_keys:
        if length >= k:
            symbol_l, n_extra_l = LENGTH_TABLE[k]
            extra_val = length - k
            return (symbol_l, extra_val, n_extra_l)
    return (0, 0, 0)


def get_distance_symbol_and_extra(distance: int) -> tuple:
    d_keys = sorted(DISTANCE_TABLE.keys(), reverse=True)
    for k in d_keys:
        if distance >= k:
            symbol_d, n_extra_d = DISTANCE_TABLE[k]
            extra_val = distance - k
            return (symbol_d, extra_val, n_extra_d)
    return (0, 0, 0)


def generate_events(tokens: list) -> list:
    events = []

    for t in tokens:
        token_type = t[0]

        if token_type == "literal":
            value = t[1]
            # convert literal into ASCII Value
            if isinstance(value, str):
                value = ord(value)
            events.append(value)

        elif token_type == "match":
            length = t[1]
            distance = t[2]

            # Process Length
            symbol_l, extra_val_l, n_extra_l = get_length_symbol_and_extra(
                length
            )
            events.append(symbol_l)
            if n_extra_l > 0:
                events.append((extra_val_l, n_extra_l))

            # Process Distance
            symbol_d, extra_val_d, n_extra_d = get_distance_symbol_and_extra(
                distance
            )
            events.append(symbol_d)
            if n_extra_d > 0:
                events.append((extra_val_d, n_extra_d))

    events.append(256)  # End of block symbol
    return events
