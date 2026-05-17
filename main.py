# Files import
import lz77
import huffman
import bit_utils
import deflate

# Libraries import
import sys
import os
import time

# Colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def format_size(n: int) -> str:
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
    start = time.perf_counter()
    in_name = os.path.basename(input_path)
    out_name = os.path.basename(output_path)

    print(f"\n{BLUE}{BOLD}📦 Compressing '{CYAN}{in_name}{BLUE}' ➔ " +
          f"'{CYAN}{out_name}{BLUE}'{RESET}")
    print(f"{WHITE}⚙️  Initializing DEFLATE-inspired pipeline...{RESET}")

    # Read the input file as raw bytes.
    with open(input_path, "rb") as input_file:
        data = input_file.read()

    # Stage 1 (LZ77): Find matching byte sequences.
    print(f"{MAGENTA}├── 🔍 {RESET}Running LZ77 pattern detection " +
          "(3-byte hashing)...", flush=True)
    tokens = lz77.lz77_compression(data)

    # Stage 2 (Deflate): Convert tokens to standard events.
    print(f"{MAGENTA}├── 🔄 {RESET}Converting LZ77 tokens to DEFLATE " +
          "standard events...", flush=True)
    events = deflate.generate_events(tokens)

    # Stage 3 (Huffman): Build Canonical Huffman Codes.
    print(f"{MAGENTA}├── 🌿 {RESET}Generating Huffman trees and " +
          "canonical codes...", flush=True)
    literal_freq, distance_freq = huffman.count_frequencies(events)

    # Build Huffman tree to calculate code length (returns sorted tuples).
    sorted_lit_lengths = huffman.build_huffman_lengths(literal_freq)
    sorted_dist_lengths = huffman.build_huffman_lengths(distance_freq)

    # Generate final codes using the tuples.
    literal_codes = huffman.generate_canonical_codes(sorted_lit_lengths)
    distance_codes = huffman.generate_canonical_codes(sorted_dist_lengths)

    # Convert tuples to fixed-size lists (286 and 30) for the bit writer.
    full_lit_lengths = huffman.get_fixed_lengths_array(sorted_lit_lengths, 286)
    full_dist_lengths = huffman.get_fixed_lengths_array(
                        sorted_dist_lengths, 30
                        )

    # Stage 4 (Bit Utils): Pack bits and write to disk.
    print(f"{MAGENTA}└── 📥 {RESET}Packing payload into destination file...",
          flush=True)
    bit_utils.write_compressed_file(output_path, full_lit_lengths,
                                    full_dist_lengths, events, literal_codes,
                                    distance_codes
                                    )

    elapsed = time.perf_counter() - start

    # Make size comparison.
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    if original_size > 0:
        ratio = (1 - compressed_size / original_size) * 100
    else:
        ratio = 0

    print(f"\n{GREEN}{BOLD}✅ Compression completed successfully!{RESET}")
    print(f"\n{CYAN}📊 Statistics:{RESET}")
    print(f"{WHITE}-------------------------------------------------{RESET}")

    orig_readable = format_size(original_size)
    comp_readable = format_size(compressed_size)

    print(f"  {WHITE}Original Size:   {YELLOW}{orig_readable:<10} " +
          f"({original_size:,} bytes){RESET}")
    print(f"  {WHITE}Compressed Size: {YELLOW}{comp_readable:<10} " +
          f"({compressed_size:,} bytes){RESET}")

    if ratio >= 0:
        print(f"  {WHITE}Space Saved:     {GREEN}{BOLD}{ratio:.1f}% 🔥{RESET}")
    else:
        print(f"  {WHITE}Size Added:      {RED}{BOLD}{abs(ratio):.1f}% ⚠️  " +
              f"(Already compressed?){RESET}")

    print(f"  {WHITE}Time Taken:      {CYAN}{elapsed:.2f} seconds ⚡{RESET}")
    print(f"{WHITE}-------------------------------------------------{RESET}\n")


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
    start = time.perf_counter()
    in_name = os.path.basename(input_path)
    out_name = os.path.basename(output_path)

    print(f"\n{BLUE}{BOLD}🗃️  Decompressing '{CYAN}{in_name}{BLUE}' ➔ " +
          f"'{CYAN}{out_name}{BLUE}'{RESET}")
    print(f"{WHITE}⚙️  Initializing DEFLATE-inspired reverse pipeline..." +
          f"{RESET}")

    try:
        # Stage 1 (Bit_utils): Read the compressed file and its header.
        print(f"{MAGENTA}├── 🔑 {RESET}Reading file header and " +
            "extracting bitstream...", flush=True)
        literal_lengths, distance_lengths, payload_bits = (
            bit_utils.read_compressed_file(input_path)
        )

        # Stage 2 (Huffman): Construct codes.
        print(f"{MAGENTA}├── 🌿 {RESET}Reconstructing Canonical Huffman " +
            "dictionaries...", flush=True)
        literal_codes = huffman.generate_codes_from_array(literal_lengths)
        distance_codes = huffman.generate_codes_from_array(distance_lengths)

        # Stage 3 (Deflate): Bit decoding of Tokens.
        print(f"{MAGENTA}├── 🔄 {RESET}Decoding bitstream back into " +
            "standard events...", flush=True)
        events = deflate.decode_bitstream(
            payload_bits, literal_codes, distance_codes
            )
        tokens = deflate.decode_events(events)

        # Stage 4 (LZ77): Decompress the LZ77.
        print(f"{MAGENTA}└── 💾 {RESET}Reconstructing original raw bytes via " +
            "LZ77 decompression...", flush=True)
        original_data = lz77.lz77_decompression(tokens)

        # Writing the original file to the hard disk
        with open(output_path, "wb") as original_file:
            original_file.write(original_data)

    except Exception as e:
        print(f"{RED}{BOLD}❌  An unexpected error occurred: {e}{RESET}")
        return

    elapsed = time.perf_counter() - start

    # Make size comparison.
    compressed_size = os.path.getsize(input_path)
    original_size = os.path.getsize(output_path)

    if compressed_size > 0:
        ratio = ((original_size - compressed_size) / compressed_size) * 100
    else:
        ratio = 0

    print(f"\n{GREEN}{BOLD}✅ Decompression completed successfully!{RESET}")
    print(f"\n{CYAN}📊 Statistics:{RESET}")
    print(f"{WHITE}-------------------------------------------------{RESET}")

    comp_readable = format_size(compressed_size)
    orig_readable = format_size(original_size)

    print(f"  {WHITE}Compressed Size: {YELLOW}{comp_readable:<10} " +
          f"({compressed_size:,} bytes){RESET}")
    print(f"  {WHITE}Original Size:   {YELLOW}{orig_readable:<10} " +
          f"({original_size:,} bytes){RESET}")

    print(f"  {WHITE}Expansion:       {GREEN}{BOLD}+{ratio:.1f}% 📈{RESET}")

    print(f"  {WHITE}Time Taken:      {CYAN}{elapsed:.4f} seconds ⚡{RESET}")
    print(f"{WHITE}-------------------------------------------------{RESET}\n")


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
            print(f"{RED}⚠️  Warning: input already looks compressed " +
                  f"(.sdfl).{RESET}")
            return

        output_path = input_path + ".sdfl"

        if os.path.exists(output_path):
            print(f"\n{YELLOW}⚠️  Warning: The file '{output_path}' " +
                  f"already exists.{RESET}")
            print(f"{WHITE}Please choose an action:{RESET}")
            print(f"  {CYAN}[1]{RESET} Abort compression (Stop)")
            print(f"  {CYAN}[2]{RESET} Overwrite the existing file")
            print(f"  {CYAN}[3]{RESET} Create a new copy automatically")

            choice = input(f"{YELLOW}> {RESET}").strip()

            if choice == '2':
                print(f"{RED}⚠️  Overwriting existing file...{RESET}")
                time.sleep(0.5)

            elif choice == '3':
                # Auto-rename logic: e.g., test.pdf -> test_copy(1).pdf
                base_name, ext = os.path.splitext(output_path)
                counter = 1
                new_output_path = f"{base_name}_copy({counter}){ext}"

                # Keep incrementing the counter until we find a free name
                while os.path.exists(new_output_path):
                    counter += 1
                    new_output_path = f"{base_name}_copy({counter}){ext}"

                output_path = new_output_path
                print(f"{GREEN}✅ Redirecting output to: " +
                      f"'{output_path}'{RESET}")

            else:
                # If user types 1 or anything else, abort for safety
                print(f"{RED}❌ Compression aborted by user.{RESET}\n")
                return

        try:
            compress_file(input_path, output_path)

        except FileNotFoundError:
            print(f"{RED}{BOLD}❌  Error: the file '{input_path}' was not " +
                  f"found. Please check the name and try again.{RESET}")
            return

        # Handles any another type of errors e.g., Invalid or corrupted file.
        except Exception as e:
            print(f"{RED}{BOLD}❌  An unexpected error occurred: {e}{RESET}")
            return

    # file decompression
    elif command == "-d":
        # Validate file's extension.
        if not input_path.endswith(".sdfl"):
            print(f"{RED}❌  Error: Input file should have .sdfl extension " +
                  f"{RESET}")
            return

        dir_name = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)

        # Remove .sdfl extension
        clean_file_name = file_name[:-5]

        # Remove _copy if exist
        if "_copy(" in clean_file_name:
            # Separate the name before _copy(
            parts = clean_file_name.split("_copy(")
            # Take the first part before _copy(
            base_part = parts[0]

            output_path = os.path.join(dir_name, base_part)

        else:
            output_path = os.path.join(dir_name, clean_file_name)

        if not os.path.exists(input_path):
            print(f"{RED}❌  Error: the file '{input_path}' was not found. " +
                  f"Please check the name and try again.{RESET}")
            return

        if os.path.exists(output_path):
            print(f"\n{YELLOW}⚠️  Warning: The file '{output_path}' " +
                  f"already exists.{RESET}")
            print(f"{WHITE}Please choose an action:{RESET}")
            print(f"  {CYAN}[1]{RESET} Abort decompression (Stop)")
            print(f"  {CYAN}[2]{RESET} Overwrite the existing file")
            print(f"  {CYAN}[3]{RESET} Create a new copy automatically")

            choice = input(f"{YELLOW}> {RESET}").strip()

            if choice == '2':
                print(f"{RED}⚠️  Overwriting existing file...{RESET}")
                time.sleep(0.5)

            elif choice == '3':
                # Auto-rename logic: e.g., test.pdf -> test_copy(1).pdf
                base_name, ext = os.path.splitext(output_path)
                counter = 1
                new_output_path = f"{base_name}_copy({counter}){ext}"

                # Keep incrementing the counter until we find a free name
                while os.path.exists(new_output_path):
                    counter += 1
                    new_output_path = f"{base_name}_copy({counter}){ext}"

                output_path = new_output_path
                print(f"{GREEN}✅ Redirecting output to: " +
                      f"'{output_path}'{RESET}")

            else:
                # If user types 1 or anything else, abort for safety
                print(f"{RED}❌ Decompression aborted by user.{RESET}\n")
                return

        try:
            decompress_file(input_path, output_path)

        except FileNotFoundError:
            print(f"{RED}{BOLD}❌  Error: the file '{input_path}' was not " +
                  f"found. Please check the name and try again.{RESET}")
            return

        # Handles any another type of errors e.g., Invalid or corrupted file.
        except Exception as e:
            print(f"{RED}{BOLD}❌  An unexpected error occurred: {e}{RESET}")
            return

    else:
        print("❌ Invalid command! Please use '-c' to compress" +
              " or '-d' to decompress.")


if __name__ == "__main__":
    try:
        main()
    # exit handling for KeyboardInterrupt (Ctrl+C) to prevent crash tracebacks.
    except KeyboardInterrupt:
        print(f"\n\n{RED}{BOLD}❌ Operation cancelled by user (Ctrl+C). " +
              f"Exiting gracefully...{RESET}")
        sys.exit(0)
