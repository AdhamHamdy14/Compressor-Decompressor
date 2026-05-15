"""
A Simplified DEFLATE Compressor and Decompressor

Student_1: Adham Hamdy Mohamed Mohamed    ID: 24010094
Student_2: Anas Alaa Abdo                 ID: 24010004
Student_3: Badr Ashraf Badry Amir         ID: 24010134
Student_4: Omar Ayman Ahmed Abd-Elmoniem  ID: 24010441
Student_5: Amr Ahmed Mahmoud Mohamed      ID: 24010479
CSED28++
"""
# Files import
import lz77
import huffman
import bit_utils
import deflate

import sys
import os
import time


def format_size(n: int) -> int:
    """
    Helper function to format the size of the file into
        a human-readable string.

    Args:
        n (int): Size of the file in bytes

    Returns:
        str: A formatted string representing the file size with its
             appropriate unit
    """
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def compress_file(input_path, output_path):
    """
    Orchestrates the entire compression pipeline to create an '.sdfl'
    compressed archive from a raw input file.

    This function executes the compression process sequentially:
    1. Reads the raw bytes from the input file.
    2. Applies LZ77 compression to find repeating byte patterns and
       generate tokens.
    3. Converts tokens into standard events (Literals, Matches, and EndEvent).
    4. Builds Canonical Huffman trees to generate optimal bit-codes based on
       symbol frequencies.
    5. Writes the Huffman lengths header and the packed bitstream payload to
       the destination file.
    6. Calculates and displays the compression ratio and size statistics.

    Args:
        input_path (str): The path to the original file to be compressed.
        output_path (str): The path where the compressed '.sdfl' archive will
                           be saved.

    Returns:
        None: The function writes directly to the disk and prints statistics
              to the console.
    """
    print("Initializing DEFLATE-inspired pipeline...")

    # Read the input file as raw bytes.
    with open(input_path, "rb") as input_file:
        data = input_file.read()

    # Stage 1 (LZ77): Find matching byte sequences.
    print("⚙️ Running LZ77 pattern detection (3-byte hashing)...", flush=True)
    tokens = lz77.lz77_compression(data)

    # Stage 2 (Deflate): Convert tokens to standard events.
    print("⚙️ Converting LZ77 tokens to DEFLATE standard events...",
          flush=True)
    events = deflate.generate_events(tokens)

    # Stage 3 (Huffman): Build Canonical Huffman Codes.
    print("⚙️ Generating Huffman trees and canonical codes...", flush=True)
    literal_freq, distance_freq = huffman.count_frequencies(events)

    # Build Huffman tree to calculate code length (returns sorted tuples).
    sorted_lit_lengths = huffman.build_huffman_lengths(literal_freq)
    sorted_dist_lengths = huffman.build_huffman_lengths(distance_freq)

    # Generate final codes using the tuples.
    literal_codes = huffman.generate_canonical_codes(sorted_lit_lengths)
    distance_codes = huffman.generate_canonical_codes(sorted_dist_lengths)

    # Convert tuples to fixed-size lists (286 and 30) for the bit writer.
    # Note: Make sure get_fixed_lengths_array is added in huffman.py
    full_lit_lengths = huffman.get_fixed_lengths_array(sorted_lit_lengths, 286)
    full_dist_lengths = huffman.get_fixed_lengths_array(sorted_dist_lengths, 30)

    # Stage 4 (Bit Utils): Pack bits and write to disk.
    print(f"⚙️ Packing payload into {output_path}...", flush=True)
    bit_utils.write_compressed_file(output_path, full_lit_lengths,
                                    full_dist_lengths, events, literal_codes,
                                    distance_codes)

    # Make size comparison.
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    if original_size > 0:
        ratio = (1 - compressed_size / original_size) * 100
    else:
        ratio = 0

    print("✅ Compression completed successfully!")
    print(f"📄 Original size:    {format_size(original_size)} " +
          f"({original_size:,} bytes)")
    print(f"🗜️ Compressed size:  {format_size(compressed_size)} " +
          f"({compressed_size:,} bytes)")

    if ratio >= 0:
        print(f"📉 Space saved:      {ratio:.1f}%")
    else:
        print(f"📉 Size added:       {abs(ratio):.1f}% " +
              "(File might be already compressed)")


def decompress_file(input_path, output_path):
    """
    Orchestrates the entire decompression pipeline to restore the original file
    from an '.sdfl' compressed archive.

    This function executes the decompression process in reverse order of
    compression:
    1. Reads the file header to extract Huffman code lengths and the bitstream.
    2. Reconstructs the Canonical Huffman code dictionaries.
    3. Decodes the bitstream back into LZ77 tokens (Literals and Matches).
    4. Decompresses the tokens to reconstruct the original raw bytes.
    5. Writes the raw bytes to the destination path and displays file
       statistics.

    Args:
        input_path (str): The path to the compressed input file
                          (must be .sdfl).
        output_path (str): The path where the decompressed original file will
                           be saved.

    Returns:
        None: The function writes directly to the disk and prints statistics
              to the console.
    """
    raise NotImplementedError("Decompression not yet implemented")

    # Stage 1 (Bit_utils): Read the compressed file and its header.
    literal_lengths, distance_lengths, bit_reader = (
        bit_utils.read_compressed_file(input_path)
    )

    # Stage 2 (Huffman): Construct codes.
    literal_codes = huffman.generate_canonical_codes(literal_lengths)
    distance_codes = huffman.generate_canonical_codes(distance_lengths)

    # Stage 3 (Deflate): Bit decoding of Tokens.
    tokens = deflate.decode_events(bit_reader, literal_codes, distance_codes)

    # Stage 4 (LZ77): Decompress the LZ77.
    original_data = lz77.lz77_decompress(tokens)

    # Writing the original file to the hard disk
    with open(output_path, "wb") as original_file:
        original_file.write(original_data)


    # Make size comparison.
    compressed_size = os.path.getsize(input_path)
    original_size = os.path.getsize(output_path)

    if compressed_size > 0:
        ratio = ((original_size - compressed_size) / compressed_size) * 100
    else:
        ratio = 0

    print("✅ Decompression completed successfully!")
    print(f"🗜️ Compressed size:   {format_size(compressed_size)} " +
          f"({compressed_size:,} bytes)")
    print(f"📄 Original size: {format_size(original_size)} " +
          f"({original_size:,} bytes)")
    print(f"📉 Space added:     +{ratio:.1f}%")


def main():
    # Ensure that the user has entered the correct number of parameters.
    if len(sys.argv) < 3:
        print("Usage:")
        print("  To compress:   python main.py -c file_to_compress")
        print("  To decompress: python main.py -d file_to_decompress")
        return

    command = sys.argv[1]  # -c for compression, -d for decompression.
    input_path = sys.argv[2]  # file to compress or decompress.

    # file compression
    if command == "-c":
        if input_path.endswith(".sdfl"):
            print("Warning: input already looks compressed (.sdfl). " +
                  "Continue? [y/N]")
            if input("> ").strip().lower() != "y":
                return

        output_path = input_path + ".sdfl"
        print(f"🗃️ Compressing '{input_path}' to '{output_path}' ...")

        try:
            start = time.perf_counter()
            compress_file(input_path, output_path)
            elapsed = time.perf_counter() - start
            print(f"⏱️ Time taken:       {elapsed:.2f} seconds")

        except FileNotFoundError:
            print(f"Error: the file '{input_path}' was not found. " +
                  "Please check the name and try again.")

        # Handles any another type of errors e.g., Invalid or corrupted file.
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # file decompression
    elif command == "-d":
        # Validate file's extension.
        if not input_path.endswith(".sdfl"):
            print("Error: Input file should have .sdfl extension")
            return

        output_path = input_path[:-5]  # Remove .sdfl extension
        print(f"🗃️ Decompressing '{input_path}' to '{output_path}' ...")

        try:
            start = time.perf_counter()
            decompress_file(input_path, output_path)
            elapsed = time.perf_counter() - start
            print(f"⏱️ Time taken:      {elapsed:.2f} seconds")

        except FileNotFoundError:
            print(f"Error: the file '{input_path}' was not found. " +
                  "Please check the name and try again.")

        # Handles any another type of errors e.g., Invalid or corrupted file.
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    else:
        print("❌ Invalid command! Please use '-c' to compress" +
              " or '-d' to decompress.")


if __name__ == "__main__":
    main()
