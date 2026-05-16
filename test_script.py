def view_file_in_binary(file_path: str, num_bytes: int = 20):
    """
    Reads a file and displays its content as raw binary (zeros and ones).

    Args:
        file_path (str): The absolute or relative path to the file.
        num_bytes (int): The maximum number of bytes to display to prevent
                         terminal clutter.
    """
    try:
        # Open the file in Read Binary ('rb') mode
        with open(file_path, 'rb') as f:
            data = f.read()

        print(f"🔍 Analyzing: {file_path}")
        print(f"📦 Total File Size: {len(data)} bytes\n")
        print("-" * 30)

        # Limit the output to the specified num_bytes to avoid overwhelming
        # the console.
        limit = min(num_bytes, len(data))

        for i in range(limit):
            byte_val = data[i]
            # Convert the byte value to an 8-bit padded binary string.
            binary_str = format(byte_val, '08b')
            print(f"Byte {i:03d} | Binary: {binary_str} | " +
                  f"Decimal: {byte_val:03d}")

        print("-" * 30)

        # Indicate if there are remaining undisplayed bytes.
        if len(data) > num_bytes:
            print(f"... and {len(data) - num_bytes} more bytes hidden.")

    except FileNotFoundError:
        print("❌ Error: File not found. Please verify the file path.")


# Specify the path to your compressed file here.
file_path = r"D:\Git_hub\Compressor-Decompressor\tests\test1.txt.sdfl"

# Display up to 78 bytes (adjust the number as needed for debugging).
view_file_in_binary(file_path, 78)
