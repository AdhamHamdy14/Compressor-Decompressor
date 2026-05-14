# 🗜️ Compressor-Decompressor 🗃️

## 📌 Description
This project is a bit-level file compressor and decompressor inspired by the widely-used **DEFLATE** algorithm. Built as a terminal-based CLI tool in Python, it operates directly on byte streams to achieve **byte-for-byte lossless compression**.

The compression pipeline is built from scratch and consists of four main stages:
1. **LZ77 Pattern Detection:** Finds and replaces repeated byte sequences with `(length, distance)` matches using an optimized 3-byte hash dictionary.
2. **DEFLATE Symbols Generation:** Converts literals and matches into specific symbol ranges with their respective extra bits.
3. **Canonical Huffman Coding:** Generates optimal prefix codes based on symbol frequencies to minimize payload size.
4. **Custom Bitwise Payload:** Packs the computed Huffman tables and encoded data into a custom `.sdfl` format, writing the output bit-by-bit.

---

## 👥 Contributors
This project was developed by Computer and Systems Engineering Department (CSED28++) students at **Alexandria University - Faculty of Engineering**:

* **Anas Alaa Abdo** (ID: `24010004`) - [GitHub Profile](https://github.com/AnasAlaa11)
* **Adham Hamdy Mohamed Mohamed** (ID: `24010094`) - [GitHub Profile](https://github.com/AdhamHamdy14)
* **Badr Ashraf Badry Amir** (ID: `24010134`) - [GitHub Profile](https://github.com/BadrAshraf20)
* **Omar Ayman Ahmed Abd-Elmoniem** (ID: `24010441`) - [GitHub Profile](https://github.com/OmarAyman879)
* **Amr Ahmed Mahmoud Mohamed** (ID: `24010479`) - [GitHub Profile](https://github.com/AmrAhmed292)

---

## 📁 Repository Structure
* [`main.py`](./main.py): The primary entry point of the application. It handles CLI arguments and orchestrates the overall compression and decompression workflows.
* [`lz77.py`](./lz77.py): Implementation of the LZ77 sliding window algorithm, responsible for finding duplicated strings and performing dictionary-based compression.
* [`deflate.py`](./deflate.py): The core integration layer that combines LZ77 and Huffman encoding to achieve high-efficiency compression (similar to the DEFLATE standard).
* [`huffman.py`](./huffman.py): Contains the Huffman Coding logic, including building frequency trees and generating prefix-free binary codes for data blocks.
* [`bit_utils.py`](./bit_utils.py): A utility module for low-level bit manipulation, providing functions to read and write data at the bit level rather than bytes.

---

## Data Overflow
The input data flows through a structured pipeline to achieve efficient compression, following the DEFLATE standard. This workflow is orchestrated by `deflate.py` which manages the data transfer between the LZ77 and Huffman stages.
![Workflow](./docs/workflow.png)

### Pipeline Description:
1.  **Input Data:** The raw byte stream of the file to be compressed.
2.  **`lz77.py` (Pre-compression):** Scans for repeated data patterns, outputting a mix of raw literals and (distance, length) pairs.
3.  **`deflate.py` (The Orchestrator):** Acts as the main integration layer. It receives processed data from `lz77.py`, decides on the Huffman tree configuration (static vs dynamic), and manages the encoding flow.
4.  **`huffman.py` (Entropy Coding):** Generates optimized prefix codes for the literals and distances received from the previous stage.
5.  **`bit_utils.py` (Packing):** The final stage that packs variable-length Huffman codes into a compact binary stream and writes the final compressed file.

---

## 🚀 How to Run

### 1. Prerequisites
Ensure you have Python 3 installed on your machine.


### 2. Usage Instructions
The tool provides a simple Command Line Interface (CLI) to manage your files. Follow these patterns to use the compressor and decompressor effectively:

#### 1. Compression
To compress a file using the DEFLATE-inspired pipeline, use the `-c` (compress) flag. This will generate a `.sdfl` file in the same directory.
```bash
python main.py -c <input_file_path>
```
Example: python main.py -c document.txt
Output: A compressed file named document.txt.sdfl.

#### 2. Decompression
To restore a `.sdfl` file to its original state, use the `-d` (decompress) flag.
```bash
python main.py -d <compressed_file_path>
```
Example: python main.py -d document.txt.sdfl
Output: The original file is reconstructed with its initial content.

---

## 🧠 How it Works (The Math behind the Magic)
Our compression engine relies on a powerful two-step combination of dictionary-based string matching and statistical entropy coding, firmly rooted in **Information Theory**.

### 1. LZ77 (Spatial Redundancy Elimination)
LZ77 utilizes a sliding window approach divided into a **Search Buffer** (history) and a **Lookahead Buffer** (upcoming data). Instead of storing repetitive byte sequences, the algorithm encodes them as a reference tuple: `<Distance, Length>`.
For instance, if the sequence "CSED" appeared 20 bytes ago and is 4 bytes long, it is encoded simply as `<20, 4>`. This transforms spatial redundancy into highly compact pointers.

### 2. Huffman Coding (Entropy Optimization)
According to Claude Shannon's Source Coding Theorem, the theoretical lower bound for the average length of a compressed symbol is defined by its Entropy $H(X)$:

$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

Where $P(x_i)$ is the probability (or frequency) of symbol $x_i$ appearing in the data stream.

To approach this optimal limit, we use **Canonical Huffman Coding**. It builds a binary tree prioritizing higher-frequency symbols. Frequent symbols are assigned shorter bit sequences (e.g., `01`), while rare symbols receive longer ones (e.g., `11010`). Because the generated binary codes are **Prefix-Free** (no code is a prefix of any other), the continuous bit-stream can be unambiguously decoded without needing separators.
---

## 💻 Example Output
Here is a glimpse of what the terminal output looks like during a successful execution cycle:

### Compression Cycle
### Decompression Cycle
