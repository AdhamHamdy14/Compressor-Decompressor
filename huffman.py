import heapq


class Node:
    def __init__(self, symbol, freq, left=None, right=None):
        """
        Initialize a Huffman tree node.

        Args:
            symbol: The actual symbol for leaves, or dummy for internal nodes.
            freq: Frequency of the symbol(s).
            left: Pointer to the left child node.
            right: Pointer to the right child node.
        """

        # The actual symbol for leaves, or a dummy for internal nodes.
        self.symbol = symbol
        self.freq = freq      # Frequency of the symbol(s).
        self.left = left      # Pointer to the left child node.
        self.right = right    # Pointer to the right child node.

        # Determine the minimum symbol in this subtree for
        # deterministic tie-breaking.
        if left is None and right is None:
            # Leaf node: the minimum symbol is its own symbol.
            self.min_symbol = symbol
        else:
            # Internal node: the minimum symbol is the smallest between
            # its left and right children.
            self.min_symbol = min(left.min_symbol, right.min_symbol)

    # Magic method to define the "Less Than" (<) operator for
    # the Priority Queue.
    def __lt__(self, other):
        """
        Compare two nodes for Priority Queue ordering.

        Sorting is based primarily on symbol frequency (ascending).
        In case of a tie, the minimum symbol value within the subtree
        is used as a tie-breaker to ensure deterministic tree construction.

        Args:
            other (Node): The other Huffman tree node to compare against.

        Returns:
            bool: True if this node is considered "less than" the other node.
        """

        # 1. Primary comparison: Sort by frequency (ascending).
        if self.freq != other.freq:
            return self.freq < other.freq

        # 2. Secondary comparison (Tie-breaker): If frequencies are equal,
        # break the tie using the smallest symbol value inside the subtree.
        return self.min_symbol < other.min_symbol


def count_frequencies(events: list) -> tuple:
    # Initialize frequency arrays
    lit_freq = [0] * 286
    dist_freq = [0] * 30
    
    # [MODIFICATION]: Replaced while loop with a clean for loop
    for event in events:
        event_type = event[0]
        
        if event_type == "Literal":
            # event format: ("Literal", symbol)
            symbol = event[1]
            lit_freq[symbol] += 1
            
        elif event_type == "Match":
            # event format: ("Match", len_sym, len_extra_str, dist_sym, dist_extra_str)
            len_sym = event[1]
            dist_sym = event[3]
            lit_freq[len_sym] += 1
            dist_freq[dist_sym] += 1
            
        elif event_type == "End":
            # event format: ("End", 256)
            lit_freq[256] += 1
            
    return lit_freq, dist_freq


def build_huffman_tree(frequencies: dict):
    """
    Build a Huffman tree from a dictionary of symbol frequencies.

    This function uses a priority queue (min-heap) to repeatedly merge the
    two nodes with the lowest frequencies until a single root node remains.

    Args:
        frequencies (dict): A dictionary mapping symbols to their frequencies.

    Returns:
        Node: The root node of the constructed Huffman tree, or None if
              the input dictionary is empty.
    """

    # 1. Create a leaf node for each symbol and add it to the priority queue.
    # The heap stores (Node) and uses Node.__lt__ to sort them.
    priority_queue = []
    for symbol, freq in frequencies.items():
        node = Node(symbol, freq)
        heapq.heappush(priority_queue, node)

    # 2. Iterate until only one node remains in the queue.
    while len(priority_queue) > 1:
        # Pull the two nodes with the lowest frequencies.
        left_child = heapq.heappop(priority_queue)
        right_child = heapq.heappop(priority_queue)

        # Create a new internal node with these two as children
        # Its frequency is the sum of their frequencies.
        parent = Node(
            'X', left_child.freq + right_child.freq, left_child, right_child
        )

        # Push the parent node back into the queue.
        heapq.heappush(priority_queue, parent)

    # 3. The remaining node is the root of the Huffman tree.
    # Return None if the dictionary was empty, else return the root.
    return priority_queue[0] if priority_queue else None


def get_bit_lengths(node, depth, lengths_dict):
    """
    Recursively traverse the Huffman tree to calculate the bit length of
    each symbol.

    The bit length corresponds to the depth of the leaf node in the tree.
    Results are populated in the provided dictionary.

    Args:
        node (Node): The current node in the Huffman tree (starts at root).
        depth (int): The current depth in the tree (starts at 0).
        lengths_dict (dict): A dictionary to store the calculated lengths
                             (modified in place).
    """

    # 1. Base Case: If the node is None, just return (safety check).
    if node is None:
        return

    # 2. Leaf Node Case: If the node has no children, it's a symbol.
    if node.left is None and node.right is None:
        # Special case: If the root is the only node, its length is 1 bit.
        lengths_dict[node.symbol] = depth if depth > 0 else 1
        return

    # 3. Recursive Step:
    # Passing 'depth + 1' by value ensures each branch knows its own depth.
    if node.left:
        get_bit_lengths(node.left, depth+1, lengths_dict)

    if node.right:
        get_bit_lengths(node.right, depth+1, lengths_dict)
# How to use it:
# lengths = {}
# get_bit_lengths(root_node, 0, lengths)


def build_huffman_lengths(frequencies: dict):
    """
    Build a Huffman tree and extract sorted bit lengths for each symbol.

    This function coordinates the tree construction, extracts the bit lengths
    using Depth First Search (DFS), and sorts the results to prepare for
    Canonical Huffman code generation.

    Args:
        frequencies (dict): A dictionary mapping symbols to their frequencies.

    Returns:
        list: A list of tuples (symbol, bit_length), sorted primarily by
              bit length (ascending) and secondarily by symbol value.
    """

    # 1. Build the deterministic Huffman tree.
    root = build_huffman_tree(frequencies)

    # 2. Extract bit lengths using DFS.
    bit_lengths = {}
    if root:
        get_bit_lengths(root, 0, bit_lengths)

    # 3. Sorting for Canonical Huffman
    # Rules: Primary sort by bit length, secondary sort by symbol value.
    # This ensures that codes are assigned in the correct order later.
    sorted_lengths = sorted(bit_lengths.items(), key=lambda x: (x[1], x[0]))

    return sorted_lengths


def generate_canonical_codes(sorted_lengths: list) -> dict:
    """
    Generate Canonical Huffman codes from sorted bit lengths.

    Calculates the exact prefix-free binary code for each symbol based on
    the DEFLATE canonical rules. The returned codes are formatted as 
    padded binary strings to ensure correct bitwise writing with leading zeros.

    Args:
        sorted_lengths (list): A sorted list of (symbol, bit_length) tuples.

    Returns:
        dict: A dictionary mapping each symbol to its binary string representation
              (e.g., "010").
    """

    # 1. Guard against empty input to prevent errors.
    if not sorted_lengths:
        return {}

    # 2. Find the maximum bit length (the highest 'floor' in our hotel analogy)
    # This determines the size of our tracking arrays.
    max_length = max(length for symbol, length in sorted_lengths)

    # 3. Count the number of symbols at each bit length.
    # count[len] will store how many symbols have exactly 'len' bits.
    count = [0] * (max_length + 1)
    for symbol, length in sorted_lengths:
        count[length] += 1

    # Length 0 means the symbol is not used in the file, so it gets 0 codes.
    count[0] = 0

    # 4. Calculate the starting code (next_code) for each bit length.
    next_code = [0] * (max_length + 1)
    code = 0
    for bits in range(1, max_length + 1):
        # The starting code for this length is calculated by taking the
        # (previous code + number of symbols at the previous length) and
        # shifting left by 1 (acting like moving down a floor, adding a 0 bit).
        code = (code + count[bits - 1]) << 1
        next_code[bits] = code

    # 5. Assign the canonical codes to each symbol.
    canonical_codes = {}
    for symbol, length in sorted_lengths:
        # Skip symbols that do not appear in the data (length 0).
        if length != 0:
            # Retrieve the current available integer code for this specific bit length.
            code_value = next_code[length]

            # [MODIFICATION]: Convert the integer to a padded binary string.
            # Storing it directly as a string (e.g., "010") fixes the BitWriter compatibility.
            binary_string = format(code_value, f"0{length}b")
            canonical_codes[symbol] = binary_string

            # Increment the code value for the next symbol that
            # shares this bit length.
            next_code[length] += 1

    return canonical_codes

def get_fixed_lengths_array(sorted_lengths: list, max_size: int) -> list:
    """
    Converts a list of (symbol, bit_length) tuples into a fixed-size list.
    """
    lengths_array = [0] * max_size
    for symbol, length in sorted_lengths:
        if symbol < max_size:
            lengths_array[symbol] = length
    return lengths_array
