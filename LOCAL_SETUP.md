# Local Setup and Execution Guide

This guide provides detailed instructions on how to set up and run the QR and Barcode Detection and Decoding system on your local machine.

## 1. Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Git
- pip (Python package installer)

## 2. Installation Steps

### Step 1: Clone the repository
Navigate to the directory where you want to store the project and run:
```bash
git clone <repository-url>
cd "QR and BarCode Detection and Decoding"
```

### Step 2: Create a virtual environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.
```bash
python3 -m venv venv
```

### Step 3: Activate the virtual environment
- **macOS and Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

### Step 4: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Install system dependencies (ZBar)
The system uses the ZBar library for decoding. This must be installed on your operating system:

- **macOS:**
  ```bash
  brew install zbar
  ```
- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install libzbar0
  ```
- **Windows:**
  Download and install the ZBar Windows installer from the official source (http://zbar.sourceforge.net/).

*Note: The codebase contains a custom fix for macOS that automatically detects the Homebrew installation path, so no additional environment variables are required.*

## 3. Verifying the Setup

To ensure everything is installed correctly, run the verification script:
```bash
python verify_setup.py
```
If the script prints "zbar shared library is correctly installed and linked", you are ready to go.

## 4. Running the System

The system is controlled via `main.py`.

### Single Image Processing
To process a single image and automatically detect whether it contains a QR code or a barcode:
```bash
python main.py --input path/to/your/image.png --type auto --visualize
```

### Batch Processing
To process an entire folder of images:
```bash
python main.py --batch --input-dir path/to/folder --output results.csv --type auto
```

### Command Line Arguments
- `--input` / `-i`: Path to a single image file.
- `--batch` / `-b`: Enables batch processing mode.
- `--input-dir`: Directory path for batch processing.
- `--type` / `-t`: Choices are `qr`, `barcode`, or `auto`.
- `--output` / `-o`: Path to save the results (CSV or JSON).
- `--visualize` / `-v`: Enables saving annotated images with bounding boxes.
- `--verbose`: Enables detailed debug logging.

## 5. Running Tests

To run the automated test suite and ensure all modules are functioning correctly:
```bash
# Run all tests
pytest tests/

# Run specific phase tests
python test_phase2.py
python test_phase3.py
```

## 6. Project Structure

- `src/detection/`: Contains logic for locating codes in images.
- `src/decoding/`: Contains logic for extracting data from detected codes.
- `src/utils/`: Shared utilities for logging, config, and visualization.
- `outputs/`: Default directory for results and visualizations.
- `config.yaml`: Global settings for the detection algorithms.
