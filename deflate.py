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

INV_LENGTH_TABLE = {
    # length_key (symbol): (base_len)
    257: 3,  258: 4,  259: 5,  260: 6,
    261: 7,  262: 8,  263: 9,  264: 10,
    265: 11, 266: 13, 267: 15, 268: 17,
    269: 19, 270: 23, 271: 27, 272: 31,
    273: 35, 274: 43, 275: 51, 276: 59,
    277: 67, 278: 83, 279: 99, 280: 115,
    281: 131, 282: 163, 283: 195, 284: 227,
    285: 258
}

INV_DISTANCE_TABLE = {
    # distance_key (symbol): (base_dist)
    0: 1,    1: 2,    2: 3,    3: 4,
    4: 5,    5: 7,    6: 9,    7: 13,
    8: 17,   9: 25,   10: 33,  11: 49,
    12: 65,  13: 97,  14: 129, 15: 193,
    16: 257, 17: 385, 18: 513, 19: 769,
    20: 1025, 21: 1537, 22: 2049, 23: 3073,
    24: 4097, 25: 6145, 26: 8193, 27: 12289,
    28: 16385, 29: 24577
}


def get_length_symbol_and_extra(length: int) -> tuple:
    """
    Finds the DEFLATE symbol and extra bits for a given match length.

    It searches the LENGTH_TABLE to find the correct base length,
    calculates the difference (extra value), and returns the data needed
    for Huffman coding.

    Args:
        length (int): The original match length from LZ77.

    Returns:
        tuple: (length_symbol, extra_value, number_of_extra_bits)
    """
    l_keys = sorted(LENGTH_TABLE.keys(), reverse=True)
    for k in l_keys:
        if length >= k:
            symbol_l, n_extra_l = LENGTH_TABLE[k]
            extra_val = length - k
            return (symbol_l, extra_val, n_extra_l)
    return (0, 0, 0)


def get_distance_symbol_and_extra(distance: int) -> tuple:
    """
    Finds the DEFLATE symbol and extra bits for a given match distance.

    It searches the DISTANCE_TABLE to find the correct base distance,
    calculates the difference (extra value), and returns the data needed
    for Huffman coding.

    Args:
        distance (int): The original match distance from LZ77.

    Returns:
        tuple: (distance_symbol, extra_value, number_of_extra_bits)
    """
    d_keys = sorted(DISTANCE_TABLE.keys(), reverse=True)
    for k in d_keys:
        if distance >= k:
            symbol_d, n_extra_d = DISTANCE_TABLE[k]
            extra_val = distance - k
            return (symbol_d, extra_val, n_extra_d)
    return (0, 0, 0)


def generate_events(tokens: list) -> list:
    """
    Converts a list of LZ77 tokens into a list of formatted DEFLATE events.

    This is the main compression function for this stage. It processes
    literal characters and matches, formats the extra bits into padded
    binary strings, and adds the End-of-Block symbol at the end.

    Args:
        tokens (list): A list of LZ77 tokens, e.g., [("Literal", "a"),
        ("Match", 4, 1)].

    Returns:
        list: A list of formatted events ready for the Huffman and
        Writer stages.
    """
    events = []

    for t in tokens:
        token_type = t[0]

        if token_type == "Literal":
            value = t[1]
            # convert literal into ASCII Value
            if isinstance(value, str):
                value = ord(value)
            events.append(("Literal", value))

        elif token_type == "Match":
            length = t[1]
            distance = t[2]

            # Process Length
            symbol_l, extra_val_l, n_extra_l = get_length_symbol_and_extra(
                length
            )
            # Process Distance
            symbol_d, extra_val_d, n_extra_d = get_distance_symbol_and_extra(
                distance
            )
            str_ex_l = format(
                extra_val_l, f'0{n_extra_l}b') if n_extra_l > 0 else ""
            str_ex_d = format(
                extra_val_d, f'0{n_extra_d}b') if n_extra_d > 0 else ""
            events.append(("Match", symbol_l, str_ex_l, symbol_d, str_ex_d))

    events.append(("End", 256))  # End of block symbol
    return events


def get_actual_length(len_sym: int, len_extra_str: str) -> int:
    """
    Reconstructs the original match length during decompression.

    It looks up the base length using the Huffman symbol and adds the
    integer value of the binary extra bits string.

    Args:
        len_sym (int): The decoded Huffman length symbol.
        len_extra_str (str): The binary string of extra bits.

    Returns:
        int: The exact original match length.
    """
    base_len = INV_LENGTH_TABLE[len_sym]

    # Convert len_extra_str to an integer number
    extra_len_val = int(len_extra_str, 2) if len_extra_str else 0

    return base_len + extra_len_val


def get_actual_distance(dist_sym: int, dist_extra_str: str) -> int:
    """
    Reconstructs the original match distance during decompression.

    It looks up the base distance using the Huffman symbol and adds the
    integer value of the binary extra bits string.

    Args:
        dist_sym (int): The decoded Huffman distance symbol.
        dist_extra_str (str): The binary string of extra bits.

    Returns:
        int: The exact original match distance.
    """
    base_dist = INV_DISTANCE_TABLE[dist_sym]

    # Convert len_extra_str to an integer number
    extra_dist_val = int(dist_extra_str, 2) if dist_extra_str else 0

    return base_dist + extra_dist_val


def decode_events(events: list) -> list:
    """
    Convert a list of decoded Huffman events back into original LZ77 tokens.

    Args:
        events (list): Decoded events from the bitstream.
                       Format: [("Literal", 97), ("Match", 257, "01", 3, "0"),
                       ("End", 256)]

    Returns:
        list: Reconstructed LZ77 tokens.
              Format: [("literal", "a"), ("match", 4, 1)]
    """
    tokens = []

    for event in events:
        kind = event[0]

        if kind == "Literal":
            tokens.append(("Literal", event[1]))

        elif kind == "Match":
            # Unpack len_sym, len_extra, dist_sym, dist_extra from event
            len_sym = event[1]
            len_extra_str = event[2]
            dist_sym = event[3]
            dist_extra_str = event[4]

            # Use inverse tables to get base_length and base_distance
            len = get_actual_length(len_sym, len_extra_str)
            dist = get_actual_distance(dist_sym, dist_extra_str)

            # Append ("match", actual_length, actual_distance) to tokens list
            tokens.append(("Match", len, dist))

        # Break the loop as the end of block is reached
        elif kind == "End":
            break

    return tokens


def decode_bitstream(
    payload_bits: str,
    lit_codes: dict,
    dist_codes: dict
) -> list:
    """
    Reads the raw payload bits and converts them back into Deflate events
    using the reconstructed Huffman canonical codes.
    """

    inv_lit = {v: k for k, v in lit_codes.items()}
    inv_dist = {v: k for k, v in dist_codes.items()}

    len_extra_bits = {sym: extra for _, (sym, extra) in LENGTH_TABLE.items()}
    dist_extra_bits = {
                      sym: extra for _, (sym, extra) in DISTANCE_TABLE.items()}

    events = []
    i = 0
    n = len(payload_bits)

    while i < n:
        current_bits = ""
        sym = None
        while i < n:
            current_bits += payload_bits[i]
            i += 1
            if current_bits in inv_lit:
                sym = inv_lit[current_bits]
                break

        if sym is None:
            break

        if sym < 256:
            events.append(("Literal", sym))

        elif sym == 256:
            events.append(("End", 256))
            break

        else:

            len_sym = sym
            n_extra_l = len_extra_bits[len_sym]

            len_extra_str = payload_bits[i:i+n_extra_l]
            i += n_extra_l

            current_bits = ""
            dist_sym = None
            while i < n:
                current_bits += payload_bits[i]
                i += 1
                if current_bits in inv_dist:
                    dist_sym = inv_dist[current_bits]
                    break

            if dist_sym is None:
                raise ValueError(
                    "Corrupted compressed file: missing distance bits.")

            n_extra_d = dist_extra_bits[dist_sym]

            dist_extra_str = payload_bits[i:i+n_extra_d]
            i += n_extra_d

            events.append((
                "Match", len_sym, len_extra_str, dist_sym, dist_extra_str))

    return events
