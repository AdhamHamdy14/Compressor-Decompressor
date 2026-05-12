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


def format_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def compress_file(input_path, output_path):
    # Read the input file as raw bytes.
    with open(input_path, "rb") as input_file:
        data = input_file.read()

    # Stage 1 (LZ77): Find matching byte sequences.
    tokens = lz77.lz77_compression(data)

    # Stage 2 (Deflate): Convert tokens to standard events.
    events = deflate.generate_events(tokens)

    # Stage 3 (Huffman): Build Canonical Huffman Codes.
    literal_freq, distance_freq = huffman.count_frequencies(events)

    # Build Huffman tree to calculate code length.
    literal_lengths = huffman.build_huffman_lengths(literal_freq)
    distance_lengths = huffman.build_huffman_lengths(distance_freq)

    # Generate final codes.
    literal_codes = huffman.generate_canonical_codes(literal_lengths)
    distance_codes = huffman.generate_canonical_codes(distance_lengths)

    # Stage 4 (Bit Utils): Pack bits and write to disk.
    bit_utils.write_compressed_file(output_path, literal_lengths,
                                    distance_lengths, events, literal_codes,
                                    distance_codes)

    # Make size comparison.
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    if original_size > 0:
        ratio = (1 - compressed_size / original_size) * 100
    else:
        ratio = 0

    print("✅ Compression completed successfully!")
    print(f"  Original size:   {format_size(original_size)}")
    print(f"  Compressed size: {format_size(compressed_size)}")

    if ratio >= 0:
        print(f"  Space saved:     {ratio:.1f}%")
    else:
        print(f"  Size added:  {abs(ratio):.1f}% " +
              "(File might be already compressed)")


def decompress_file(input_path, output_path):
    raise NotImplementedError("Decompression not yet implemented")

    # Make size comparison.
    compressed_size = os.path.getsize(input_path)
    original_size = os.path.getsize(output_path)

    if compressed_size > 0:
        ratio = ((original_size - compressed_size) / compressed_size) * 100
    else:
        ratio = 0

    print("✅ Decompression completed successfully!")
    print(f"  Compressed size:   {format_size(compressed_size)}")
    print(f"  Original size: {format_size(original_size)}")
    print(f"  Space added:     +{ratio:.1f}%")


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
            print(f"  Time taken:      {elapsed:.2f}s")

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
            print(f"  Time taken:      {elapsed:.2f}s")

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
