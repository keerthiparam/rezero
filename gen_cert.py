#!/usr/bin/env python3
"""
Generates a PDF wipe certificate using the WeasyPrint library.
This script requires WeasyPrint to be installed:
    pip install WeasyPrint
"""
import sys
import os
import datetime
import subprocess
import json
import socket

# --- WeasyPrint is a required dependency ---
try:
    from weasyprint import HTML, CSS
except ImportError:
    print("Error: WeasyPrint library not found.", file=sys.stderr)
    print("Please install it by running: pip install WeasyPrint", file=sys.stderr)
    sys.exit(1)

def get_device_details(device_path):
    """Uses lsblk to get detailed information about a block device as a pre-formatted string."""
    try:
        cmd = [
            "lsblk", "-d", "-o", "NAME,SIZE,MODEL,SERIAL,TYPE",
            "--bytes", "--json", device_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        details_json = json.loads(result.stdout)
        # Prettify the JSON for display in the PDF
        pretty_details = json.dumps(details_json['blockdevices'][0], indent=4)
        return pretty_details
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, IndexError) as e:
        return f"Could not retrieve device details for '{device_path}'.\nReason: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def generate_pdf_certificate(device_path, output_base, wipe_method, verification_hash, mode):
    """Generates the wipe certificate as a PDF file."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    hostname = socket.gethostname()
    try:
        user = os.getlogin()
    except OSError:
        user = f"uid:{os.geteuid()}"

    device_details = get_device_details(device_path)
    output_filename = f"{output_base}_certificate.pdf" # Changed to .pdf

    # --- Prepare Dry Run Banner if needed ---
    dry_run_html_banner = ""
    if mode.lower() == "dry":
        dry_run_html_banner = """
        <div class="dry-run-banner">
            <h2>DRY RUN MODE</h2>
            <p>This certificate was generated from a dry run. No destructive operations were performed on the device.</p>
        </div>
        """

    # --- Assemble the HTML Content with Embedded CSS ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Secure Data Wipe Certificate for {device_path}</title>
        <style>
            body {{
                font-family: sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #333;
            }}
            .container {{
                border: 2px solid #000;
                padding: 20px 40px;
                margin: 20px;
            }}
            h1 {{
                text-align: center;
                border-bottom: 2px solid #ccc;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 24pt;
            }}
            h2 {{
                font-size: 16pt;
                color: #555;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }}
            .dry-run-banner {{
                border: 3px dashed #d9534f;
                background-color: #f2dede;
                color: #a94442;
                padding: 10px 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .details-grid {{
                display: grid;
                grid-template-columns: 200px 1fr;
                gap: 5px 20px;
                margin-bottom: 20px;
            }}
            .details-grid b {{
                font-weight: bold;
            }}
            .mono {{
                font-family: monospace;
                background-color: #f5f5f5;
                padding: 15px;
                border: 1px solid #ccc;
                border-radius: 4px;
                white-space: pre-wrap; /* Allows long lines to wrap */
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {dry_run_html_banner}
            <h1>Secure Data Wipe Certificate</h1>

            <h2>Operation Details</h2>
            <div class="details-grid">
                <b>Wipe Timestamp (UTC):</b> <span>{timestamp}</span>
                <b>Wipe Method Employed:</b> <span>{wipe_method}</span>
                <b>Executing Hostname:</b> <span>{hostname}</span>
                <b>Executing User:</b> <span>{user}</span>
                <b>Execution Mode:</b> <span>{mode.upper()}</span>
            </div>

            <h2>Device Information</h2>
            <div class="details-grid">
                <b>Device Path:</b> <span>{device_path}</span>
            </div>
            <pre class="mono">{device_details}</pre>

            <h2>Verification</h2>
            <p>Post-wipe sample hash (SHA256) of the first 4096 bytes:</p>
            <pre class="mono">{verification_hash}</pre>
        </div>
    </body>
    </html>
    """

    # --- Write to PDF file ---
    try:
        HTML(string=html_content).write_pdf(output_filename)
        print(f"Successfully generated PDF certificate: {output_filename}")
    except Exception as e:
        print(f"Error: Could not write PDF certificate '{output_filename}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <device_path> <output_base> \"<wipe_method>\" <verification_hash> <mode>", file=sys.stderr)
        sys.exit(1)

    dev_path, out_base, method, v_hash, mode = sys.argv[1:6]
    generate_pdf_certificate(dev_path, out_base, method, v_hash, mode)
