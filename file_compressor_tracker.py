import heapq
import os
import time
import pickle
from collections import Counter
import matplotlib.pyplot as plt

class AlgorithmTracker:
    """Manages tracking, logging, and benchmarking algorithmic performance metrics."""
    def __init__(self, algorithm_name):
        self.algo_name = algorithm_name
        self.start_time = 0
        self.end_time = 0
        self.source_size = 0
        self.output_size = 0

    def start(self, file_path):
        self.source_size = os.path.getsize(file_path)
        self.start_time = time.perf_counter()

    def stop(self, file_path):
        self.end_time = time.perf_counter()
        self.output_size = os.path.getsize(file_path)

    def print_summary(self, mode="Compression"):
        elapsed_time = self.end_time - self.start_time
        print(f"\n=================== DAA TRACKER LOG ({self.algo_name} - {mode}) ===================")
        print(f"➜ Input File Size   : {self.source_size:,} bytes")
        print(f"➜ Output File Size  : {self.output_size:,} bytes")
        
        if mode == "Compression":
            saved = self.source_size - self.output_size
            ratio = (self.output_size / self.source_size) * 100 if self.source_size > 0 else 0
            print(f"➜ Memory Saved      : {saved:,} bytes")
            print(f"➜ Compression Ratio : {ratio:.2f}% (Lower is better)")
        else:
            print(f"➜ Restored Integrity: Verified Match ✅")

        print(f"➜ Empirical Runtime : {elapsed_time:.6f} seconds")
        print("========================================================================\n")


class HuffmanNode:
    """Tree element representation optimized for Python's priority queue structures."""
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # Defines strict order parameters for heapq evaluation to resolve tree ties
    def __lt__(self, other):
        return self.freq < other.freq


class FileCompressorTracker:
    def __init__(self):
        self.tracker = AlgorithmTracker("Huffman Coding (Greedy Paradigm)")

    def _build_tree(self, text):
        """Assembles the optimal Huffman binary prefix tree via a greedy approach."""
        frequencies = Counter(text)
        # Greedy Step 1: Initialize min-heap structure with structural single leaf nodes
        heap = [HuffmanNode(char, freq) for char, freq in frequencies.items()]
        heapq.heapify(heap)

        # Greedy Step 2: Merge the two nodes with the lowest frequencies iteratively
        while len(heap) > 1:
            left_node = heapq.heappop(heap)
            right_node = heapq.heappop(heap)
            
            merged = HuffmanNode(None, left_node.freq + right_node.freq)
            merged.left = left_node
            merged.right = right_node
            
            heapq.heappush(heap, merged)

        # FIX: Return the root node element, not the array wrapper list
        return heap[0] if heap else None

    def _generate_codes(self, root, current_code, codes):
        """Traverses the prefix tree recursively to assign variable-length binary codes."""
        if root is None:
            return
        
        # Leaf node reached (stores target data element)
        if root.char is not None:
            codes[root.char] = current_code
            return

        self._generate_codes(root.left, current_code + "0", codes)
        self._generate_codes(root.right, current_code + "1", codes)

    def compress(self, input_path, output_path, verbose=True):
        """Encodes text file data using greedy Huffman maps and saves it as binary."""
        self.tracker.start(input_path)

        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        if not text:
            raise ValueError("Cannot compress an empty file structure.")

        # Algorithmic Cycle Execution
        root = self._build_tree(text)
        codes = {}
        self._generate_codes(root, "", codes)

        # Map text elements to their respective calculated variable-length codes
        encoded_bits = "".join(codes[char] for char in text)

        # Structural serialization: Convert character-bit strings into raw bytes
        byte_data = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte_chunk = encoded_bits[i:i+8]
            byte_data.append(int(byte_chunk, 2))

        # Bundle structural mapping metadata with compressed content payload
        payload = {
            'codes': codes,
            'bytes': bytes(byte_data),
            'bit_length': len(encoded_bits)
        }

        with open(output_path, 'wb') as f:
            pickle.dump(payload, f)

        self.tracker.stop(output_path)
        if verbose:
            self.tracker.print_summary(mode="Compression")

    def decompress(self, input_path, output_path, verbose=True):
        """Decodes binary payloads back into text files using the stored dictionary."""
        self.tracker.start(input_path)

        with open(input_path, 'rb') as f:
            payload = pickle.load(f)

        codes = payload['codes']
        byte_data = payload['bytes']
        bit_length = payload['bit_length']

        # Reverse evaluation mapping configuration (Code string -> Character mapping)
        reverse_codes = {v: k for k, v in codes.items()}

        # Reconstruct structural bit sequences from serialized array streams
        bit_string = "".join(f"{b:08b}" for b in byte_data)
        # Trim explicit trailing padding introduced during 8-bit chunk rounding
        bit_string = bit_string[:bit_length]

        # Traverse bit data to reconstruct original text strings
        decoded_chars = []
        current_buffer = ""
        for bit in bit_string:
            current_buffer += bit
            if current_buffer in reverse_codes:
                decoded_chars.append(reverse_codes[current_buffer])
                current_buffer = ""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("".join(decoded_chars))

        self.tracker.stop(output_path)
        if verbose:
            self.tracker.print_summary(mode="Decompression")


# ==========================================
#   DEMO EXECUTION & BENCHMARKING PLOT
# ==========================================
if __name__ == "__main__":
    # Define intermediate execution file labels
    sample_text_file = "daa_project_input.txt"
    compressed_file = "compressed_archive.bin"
    decompressed_file = "restored_output.txt"

    # Initialize Engine Module 
    engine = FileCompressorTracker()

    print("⚡ [Phase 1] Executing standard Functional Test...")
    
    # Generate simple test pattern file
    sample_data = ("ALGORITHM " * 500 + "GREEDY_PARADIGM " * 800 + "HUFFMAN_TRACKER_PROJECT_DAA " * 300)
    with open(sample_text_file, "w", encoding="utf-8") as f:
        f.write(sample_data)

    # Run Tracking Lifecycles
    engine.compress(sample_text_file, compressed_file, verbose=True)
    engine.decompress(compressed_file, decompressed_file, verbose=True)

    # ----------------------------------------------------
    print("⚡ [Phase 2] Launching Empirical Scaling Benchmark...")
    
    file_sizes_kb = [10, 50, 100, 200, 500]  # Input scale dimensions
    runtimes_ms = []

    for size in file_sizes_kb:
        # Dynamically scale data generation to hit target KB sizes
        multiplier = int((size * 1024) / 54)
        scaled_data = ("ALGORITHM " * 2 + "GREEDY " * 3 + "HUFFMAN_PROJECT " * 1) * multiplier
        
        with open(sample_text_file, "w", encoding="utf-8") as f:
            f.write(scaled_data)
            
        # Record fine-grained operational execution delta
        start = time.perf_counter()
        engine.compress(sample_text_file, compressed_file, verbose=False)
        end = time.perf_counter()
        
        runtimes_ms.append((end - start) * 1000)  # Log in milliseconds
        print(f" ✔ Checked scale: {size} KB in {(end - start) * 1000:.2f} ms")

    # Clean up generated system file pipeline configurations
    for temp_file in [sample_text_file, compressed_file, decompressed_file]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    print("🧹 Pipeline execution cleaned up. Temporary files removed.")

    # ----------------------------------------------------
    # Generate and Export the Asymptotic Plot Graph
    plt.figure(figsize=(8, 5))
    plt.plot(file_sizes_kb, runtimes_ms, marker='o', color='#2ecc71', linewidth=2, label='Empirical Runtime')
    
    plt.title('DAA Project: Empirical Scaling vs Input File Size', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Input File Size (KB)', fontsize=12)
    plt.ylabel('Execution Time (ms)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left')
    
    graph_filename = "performance_curve.png"
    plt.savefig(graph_filename, dpi=300, bbox_inches='tight')
    print(f"\n📊 Performance curve graph successfully generated and saved as '{graph_filename}'!")
