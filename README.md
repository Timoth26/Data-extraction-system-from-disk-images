# Disk Image Analyzer

A comprehensive forensic analysis tool for extracting and analyzing personal data from disk images. This system mounts disk images, detects operating systems, extracts sensitive information using AI-powered analysis, and generates detailed forensic reports.

## Features

### Core Capabilities
- **Disk Image Mounting**: Automatic mounting of disk images using loop devices
- **OS Detection**: Supports Linux, Windows, and macOS operating systems
- **User Detection**: Identifies system users across different OS types
- **Multi-format Analysis**: Supports analysis of various file formats

### Analysis Modules
- **AI-Powered PII Detection**: Uses NER model (`lakshyakh93/deberta_finetuned_pii`) to identify personal data
- **Email Extraction**: Regex-based email address extraction from multiple file types
- **Social Media Analysis**: Extracts browsing history and cookies from popular browsers
- **OCR Support**: Text extraction from images using EasyOCR
- **Statistical Analysis**: Generates charts and statistics about collected data

### Supported File Types
- **Documents**: PDF, DOCX, DOC, TXT, MD, ODT
- **Web Files**: HTML, XML, LOG, EML
- **Data Files**: CSV, JSON, PPTX, MSG, EPUB
- **Databases**: SQLite, DB files
- **Images**: PNG, JPEG, JPG (OCR)

## Installation

### Prerequisites
- Python 3.8+
- Docker (optional but recommended)
- CUDA-compatible GPU (optional, for faster AI processing)

### Native Installation

1. Clone the repository:
```bash
git clone https://github.com/Timoth26/Data-extraction-system-from-disk-images.git
cd Data-extraction-system-from-disk-images
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng
sudo apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
```

### Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/Timoth26/Data-extraction-system-from-disk-images.git
cd Data-extraction-system-from-disk-images
```

2. Build and setup:
```bash
chmod +x setup.sh run_analysis.sh
./setup.sh
```

## Usage

### Command Line Arguments

```bash
python main.py <image_path> [OPTIONS]
```

#### Required Arguments
- `image_path`: Path to the disk image file

#### Optional Arguments
- `--name`: First name for report metadata
- `--surname`: Surname for report metadata  
- `--nr`: Unique identifier for the report
- `-a, --analyze`: Enable AI analysis of text files
- `-x, --extend`: Enable extended AI analysis (more file types)
- `-e, --emails`: Enable email extraction
- `-o, --ocr`: Enable OCR on images
- `-s, --social`: Enable social media data extraction
- `-r, --sys_dir_analysis`: Include system directories (disabled by default)
- `-t, --tech_info`: Collect technical filesystem information

### Examples

#### Basic Analysis
```bash
python main.py /path/to/disk.img --name John --surname Doe --nr 001
```

#### Comprehensive Analysis
```bash
python main.py /path/to/disk.img \
    --name John --surname Doe --nr 001 \
    -a -x -e -o -s -t
```

#### Email and Social Media Focus
```bash
python main.py /path/to/disk.img \
    --name Jane --surname Smith --nr 002 \
    -e -s
```

### Docker Usage

#### Quick Analysis
```bash
./run_analysis.sh /path/to/disk.img --name John --surname Doe --nr 001 -a -e -s
```

#### Manual Docker Command
```bash
# Create required directories
mkdir -p disk_images results temp

# Copy disk image
cp your_image.img disk_images/

# Run analysis
docker-compose run --rm forensic-analyzer \
    /app/images/your_image.img \
    --name John --surname Doe --nr 001 \
    -a -x -e -o -s -t
```

## Output

The system generates several output files in the `./results/` directory:

- `report_<nr>.pdf`: Comprehensive forensic report with all findings
- `analyze_results_<nr>.txt`: Detailed AI analysis results
- `email_results_<nr>.txt`: Found email addresses
- `social_results_<nr>.txt`: Social media activity data
- `*.png`: Statistical charts and visualizations

## Architecture

### Core Components

1. **DiskImageManager** (`mount_disc.py`): Handles disk image mounting and cleanup
2. **Path Detection** (`paths.py`): OS detection, user identification, and file discovery
3. **File Analysis** (`analyze.py`): AI-powered analysis using transformers
4. **Email Finder** (`email_finder.py`): Pattern-based email extraction
5. **Social Analyzer** (`social_analyze.py`): Browser data extraction
6. **OCR Module** (`ocr.py`): Image text extraction
7. **Statistical Analysis** (`statistical_analysys.py`): Data visualization
8. **Report Generator** (`generate_report.py`): PDF report creation

### Security Considerations

- All disk images are mounted in **read-only mode**
- Temporary files are automatically cleaned up
- Loop devices are properly detached after analysis
- Analysis runs in isolated containers when using Docker

## Technical Requirements

### System Dependencies
- `sudo` access for mounting operations
- `losetup` and `mount` utilities
- Graphics libraries for OpenCV
- Tesseract OCR engine

### Python Dependencies
Key libraries include:
- `transformers`: AI model inference
- `torch`: Deep learning framework
- `opencv-python`: Image processing
- `easyocr`: OCR functionality
- `pdfplumber`: PDF text extraction
- `beautifulsoup4`: HTML parsing
- `reportlab`: PDF generation
- `matplotlib`: Data visualization