import pathlib
from tqdm import tqdm

# --- Configuration ---
# Set the name of your large, tab-separated input file
INPUT_FILE = "en-fi.txt" 
# Set the names for your output files
ENGLISH_OUTPUT_FILE = "train.en"
FINNISH_OUTPUT_FILE = "train.fi"
# Add a limit for processing. Set to None to process the entire file.
PROCESS_LIMIT = None
# ---------------------

def get_line_count(file_path):
    """Counts the number of lines in a file efficiently."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

def split_corpus_with_progress(input_path, lang1_path, lang2_path):
    """
    Reads a tab-separated parallel corpus file, splits it into two separate files,
    and displays a progress bar during the operation.

    Args:
        input_path (pathlib.Path): The path to the source file (e.g., "en-fi.txt").
        lang1_path (pathlib.Path): The path for the first language's output file (English).
        lang2_path (pathlib.Path): The path for the second language's output file (Finnish).
    """
    try:
        # Determine the total number of lines for the progress bar
        if PROCESS_LIMIT:
            total_for_progress = PROCESS_LIMIT
            print(f"Processing the first {total_for_progress:,} lines of '{input_path}'...")
        else:
            print("First, counting the total number of lines for the progress bar...")
            total_for_progress = get_line_count(input_path)
            print(f"Found {total_for_progress:,} lines in '{input_path}'. Starting the splitting process...")

        error_count = 0
        lines_processed = 0
        
        # Open all files needed. The 'with' statement ensures they are closed properly.
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(lang1_path, 'w', encoding='utf-8') as outfile_en, \
             open(lang2_path, 'w', encoding='utf-8') as outfile_fi:
            
            # Wrap the file iterator with tqdm() to create the progress bar.
            # `total` tells tqdm the scale of the bar.
            # `desc` gives the bar a descriptive label.
            progress_bar = tqdm(infile, total=total_for_progress, desc="Splitting Corpus", unit="lines")

            for line in progress_bar:
                # Stop if we have reached the processing limit
                if PROCESS_LIMIT and lines_processed >= PROCESS_LIMIT:
                    # Manually update tqdm to show 100% if we break early
                    progress_bar.n = total_for_progress
                    progress_bar.refresh()
                    break

                # Split the line at the tab character.
                parts = line.strip().split('\t')
                
                # A valid line must have exactly two parts.
                if len(parts) == 2:
                    english_text = parts[0]
                    finnish_text = parts[1]
                    
                    # Write each part to its respective file, adding a newline.
                    outfile_en.write(english_text + '\n')
                    outfile_fi.write(finnish_text + '\n')
                else:
                    # If a line is malformed, we skip it and count it as an error.
                    error_count += 1
                
                lines_processed += 1

        print("\n--- Processing Complete! ---")
        print(f"Total lines processed: {lines_processed:,}")
        processed_count = lines_processed - error_count
        print(f"Lines successfully split: {processed_count:,}")
        print(f"Lines skipped (errors): {error_count:,}")
        print(f"English sentences saved to: '{lang1_path}'")
        print(f"Finnish sentences saved to: '{lang2_path}'")

    except FileNotFoundError:
        print(f"\nError: The input file '{input_path}' was not found.")
        print("Please make sure your data file is in the same directory and is named 'en-fi.txt'.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    current_directory = pathlib.Path(__file__).parent
    
    # Create full paths for the files
    input_file_path = current_directory / INPUT_FILE
    english_file_path = current_directory / ENGLISH_OUTPUT_FILE
    finnish_file_path = current_directory / FINNISH_OUTPUT_FILE
    
    # Run the main function
    split_corpus_with_progress(input_file_path, english_file_path, finnish_file_path)

