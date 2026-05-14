"""
stage4.py — Stage 4: Custom Header and Payload (OOP implementation)
====================================================================
Provides BitWriter and BitReader helper classes for MSB-first bit-level I/O,
and the two public functions:

    write_compressed_file(output_path, lit_lengths, dist_lengths,
                          events, lit_codes, dist_codes)
    read_compressed_file(input_path) -> (lit_lengths, dist_lengths, payload_bits)
"""


# ---------------------------------------------------------------------------
# BitWriter
# ---------------------------------------------------------------------------

class BitWriter:
    """
    Accumulates bits in an internal string buffer (MSB-first) and can flush
    the buffer to a zero-padded bytearray.

    Usage
    -----
    writer = BitWriter()
    writer.write_int(2, 4)          # write the value 2 using 4 bits → "0010"
    writer.write_raw_bits("101")    # append a pre-built bit string
    data = writer.to_bytearray()    # pad to byte boundary and return bytearray
    """

    def __init__(self) -> None:
        self._bits: list[str] = []   # each element is a single '0' or '1'

    # ------------------------------------------------------------------
    def write_int(self, val: int, num_bits: int) -> None:
        """
        Append *val* as a *num_bits*-wide big-endian (MSB-first) bit string.

        Zero-padding is applied on the left so the result is always exactly
        *num_bits* characters wide.  If *num_bits* is 0 nothing is written.

        Raises
        ------
        ValueError  if *val* is negative or does not fit in *num_bits* bits.
        """
        if num_bits == 0:
            return
        if val < 0 or val >= (1 << num_bits):
            raise ValueError(
                f"Value {val} cannot be represented in {num_bits} bits."
            )
        self._bits.append(format(val, f"0{num_bits}b"))

    # ------------------------------------------------------------------
    def write_raw_bits(self, bit_str: str) -> None:
        """
        Append a pre-formed '0'/'1' string verbatim.
        Empty strings are silently ignored.
        """
        if bit_str:
            self._bits.append(bit_str)

    # ------------------------------------------------------------------
    def to_bytearray(self) -> bytearray:
        """
        Join the internal buffer, pad the tail with '0' bits until the total
        length is a multiple of 8 (MSB-first means padding goes on the right,
        filling the least-significant positions of the last byte), and return
        a bytearray.
        """
        joined = "".join(self._bits)

        remainder = len(joined) % 8
        if remainder:
            joined += "0" * (8 - remainder)

        result = bytearray(len(joined) // 8)
        for i, byte_start in enumerate(range(0, len(joined), 8)):
            result[i] = int(joined[byte_start:byte_start + 8], 2)
        return result


# ---------------------------------------------------------------------------
# BitReader
# ---------------------------------------------------------------------------

class BitReader:
    """
    Wraps a bytes object and exposes it as a seekable MSB-first bit string.

    Usage
    -----
    reader = BitReader(file_bytes)
    lit_bw  = reader.read_int(4)       # read 4 bits as an integer
    payload = reader.get_remaining_bits()  # unread bits as a '0'/'1' string
    """

    def __init__(self, data: bytes) -> None:
        # Convert every byte to its 8-bit binary representation (MSB first)
        self._bits: str = "".join(format(byte, "08b") for byte in data)
        self._pos:  int = 0

    # ------------------------------------------------------------------
    def read_int(self, num_bits: int) -> int:
        """
        Read *num_bits* from the current position and return their value as
        an unsigned integer.  The read pointer advances by *num_bits*.

        Returns 0 immediately if *num_bits* is 0.

        Raises
        ------
        EOFError  if fewer than *num_bits* bits remain.
        """
        if num_bits == 0:
            return 0
        end = self._pos + num_bits
        if end > len(self._bits):
            raise EOFError(
                f"Requested {num_bits} bits but only "
                f"{len(self._bits) - self._pos} remain."
            )
        chunk = self._bits[self._pos:end]
        self._pos = end
        return int(chunk, 2)

    # ------------------------------------------------------------------
    def get_remaining_bits(self) -> str:
        """
        Return all bits from the current position to the end of the buffer
        as a '0'/'1' string.  The read pointer is advanced to the end.

        Note: the returned string may contain trailing zero-padding that was
        added during compression.  The decompressor uses the EndEvent (symbol
        256) to know where real data stops.
        """
        remaining = self._bits[self._pos:]
        self._pos = len(self._bits)
        return remaining


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def write_compressed_file(
    output_path:  str,
    lit_lengths:  list[int],
    dist_lengths: list[int],
    events:       list[tuple],
    lit_codes:    dict[int, str],
    dist_codes:   dict[int, str],
) -> None:
    """
    Serialise the compressed data to *output_path* using the .sdfl layout:

        [4 bits]              LIT_BW
        [4 bits]              DIST_BW
        [286 × LIT_BW bits]  LIT_TABLE   — code lengths for symbols 0-285
        [30  × DIST_BW bits] DIST_TABLE  — code lengths for symbols 0-29
        [variable]           PAYLOAD     — Huffman codes + raw extra bits
        [0-7 bits]           zero-padding to reach a byte boundary

    Parameters
    ----------
    output_path  : destination file path (overwritten if it exists)
    lit_lengths  : list of 286 ints — canonical code lengths, symbols 0-285
    dist_lengths : list of 30  ints — canonical code lengths, symbols 0-29
    events       : Stage-2 event list; each event is one of:
                       ("Literal", symbol)
                       ("Match",   len_sym, len_extra, dist_sym, dist_extra)
                       ("End",     256)
    lit_codes    : dict mapping literal/length symbol → canonical bit string
    dist_codes   : dict mapping distance symbol       → canonical bit string
    """
    if len(lit_lengths) != 286:
        raise ValueError(f"lit_lengths must have 286 entries, got {len(lit_lengths)}")
    if len(dist_lengths) != 30:
        raise ValueError(f"dist_lengths must have 30 entries, got {len(dist_lengths)}")

    # ── Compute bit-widths via int.bit_length() ──────────────────────────────
    # int.bit_length() returns the number of bits needed to represent the value,
    # which equals floor(log2(M)) + 1 for M > 0, and 0 for M == 0 — exactly
    # what the spec requires.
    lit_bw  = max(lit_lengths).bit_length()
    dist_bw = max(dist_lengths).bit_length()

    writer = BitWriter()

    # ── Header ───────────────────────────────────────────────────────────────
    writer.write_int(lit_bw,  4)
    writer.write_int(dist_bw, 4)

    for length in lit_lengths:       # 286 entries
        writer.write_int(length, lit_bw)

    for length in dist_lengths:      # 30 entries
        writer.write_int(length, dist_bw)

    # ── Payload ──────────────────────────────────────────────────────────────
    for event in events:
        kind = event[0]

        if kind == "Literal":
            _, symbol = event
            writer.write_raw_bits(lit_codes[symbol])

        elif kind == "Match":
            _, len_sym, len_extra, dist_sym, dist_extra = event
            writer.write_raw_bits(lit_codes[len_sym])   # Huffman(length_symbol)
            writer.write_raw_bits(len_extra)             # raw length extra bits
            writer.write_raw_bits(dist_codes[dist_sym]) # Huffman(distance_symbol)
            writer.write_raw_bits(dist_extra)            # raw distance extra bits

        elif kind == "End":
            _, symbol = event                            # symbol is always 256
            writer.write_raw_bits(lit_codes[symbol])

        else:
            raise ValueError(f"Unknown event kind: {kind!r}")

    # ── Write to disk ─────────────────────────────────────────────────────────
    with open(output_path, "wb") as fh:
        fh.write(writer.to_bytearray())


def read_compressed_file(input_path: str) -> tuple[list[int], list[int], str]:
    """
    Read a .sdfl file and return its three logical components.

    Returns
    -------
    (lit_lengths, dist_lengths, payload_bits)
        lit_lengths  : list[int] of length 286
        dist_lengths : list[int] of length 30
        payload_bits : '0'/'1' string of all remaining bits after the header
                       (may contain trailing zero-padding; the decompressor
                       stops when it encounters the EndEvent symbol 256)
    """
    with open(input_path, "rb") as fh:
        data = fh.read()

    reader = BitReader(data)

    # ── Header ───────────────────────────────────────────────────────────────
    lit_bw  = reader.read_int(4)
    dist_bw = reader.read_int(4)

    lit_lengths: list[int] = [
        reader.read_int(lit_bw) for _ in range(286)
    ]
    dist_lengths: list[int] = [
        reader.read_int(dist_bw) for _ in range(30)
    ]

    # ── Payload ───────────────────────────────────────────────────────────────
    return lit_lengths, dist_lengths, reader.get_remaining_bits()