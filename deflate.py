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
            str_ex_l = format(extra_val_l, f'0{n_extra_l}b') if n_extra_l > 0 else ""
            str_ex_d = format(extra_val_d, f'0{n_extra_d}b') if n_extra_d > 0 else ""
            events.append(("Match", symbol_l, str_ex_l, symbol_d, str_ex_d))

    events.append(("End", 256))  # End of block symbol
    return events
