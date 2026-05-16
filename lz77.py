MIN_MATCH = 3
MAX_MATCH = 258
WINDOW_SIZE = 32768
MAX_CANDIDATES = 64


def lz77_compression(data: bytes) -> list:
    """
    Compresses data using the LZ77 algorithm.

    Iterates through the input bytes to find repeated sequences within a
    sliding window. It returns a list of tokens where each token is either
    a "literal" byte or a "match" containing (length, distance).

    Args:
        data (bytes): The raw input data to be compressed.

    Returns:
        list: A list of tuples representing compressed tokens.
              Example: [('literal', 97), ('match', 5, 10)]
    """
    size = len(data)
    table = {}
    tokens = []
    i = 0

    while i < size:

        if i + MIN_MATCH > size:

            for j in range(i, size):
                tokens.append(("Literal", data[j]))

            break

        x = data[i: i + 3]
        best_len = 0
        best_dis = 0

        candidates = table.get(x, [])

        for candidate in reversed(candidates[-MAX_CANDIDATES:]):
            distance = i - candidate

            if distance > WINDOW_SIZE:
                break

            length = 0
            while (i + length < size and
                   length < MAX_MATCH and
                   data[i + length] == data[candidate + length]):
                length += 1

            if (length > best_len
                    or (length == best_len and distance < best_dis)):
                best_len = length
                best_dis = distance

        if best_len >= MIN_MATCH:
            tokens.append(("Match", best_len, best_dis))

            for j in range(i, i + best_len):

                if j + MIN_MATCH <= size:
                    table.setdefault(data[j: j + 3], []).append(j)

            i += best_len

        else:
            tokens.append(("Literal", data[i]))
            table.setdefault(x, []).append(i)
            i += 1

    return tokens


def decompress(tokens: list) -> str:
    """
    Reconstruct the original string from a list of LZ77 tokens.

    Tokens are tuples:
        ("Literal", byte)   -> a single character
        ("match", length, distance) -> a back‑reference to previously
                                       decoded data

    The algorithm builds the output character by character, using the
    already decoded window to resolve overlapping back‑references
    automatically (e.g., 'match' can refer to data that hasn't been
    fully written yet).

    Args:
        tokens (list): A list of tuples representing the decoded LZ77 events.

    Returns:
        str: The fully reconstructed original uncompressed text.
    """
    output = []      # decoded characters
    index = 0        # current write position in 'output'

    for token in tokens:
        state = token[0]

        if state == "Literal":
            # Append the literal byte (converted to character)
            output.append(chr(token[1]))
            index += 1

        else:
            # Back‑reference: copy 'length' characters from the
            # already decoded window, starting at 'distance' bytes back
            length = token[1]
            distance = token[2]

            for _ in range(length):
                # Copy the character from the decoded window.
                # This works even if length > distance because the
                # window grows during the copy (overlapping match).
                output.append(output[index - distance])
                index += 1

    # Combine all characters into a single string
    return ''.join(output)
