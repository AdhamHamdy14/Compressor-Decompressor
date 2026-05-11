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
* `main.py`: The core python script containing the algorithm.

---

## 🚀 How to Run

### 1. Prerequisites
Ensure you have Python 3 installed on your machine.

### 2. Execution
Clone the repository, navigate to the directory, and run the script:
```bash
python main.py
```

### 3. Usage Instructions

---

## 🧠 How it Works (The Math behind the Magic)

---

## 💻 Example Output
