#!/usr/bin/env bash
set -euo pipefail

# --- Auto-detect and use a local Python virtual environment ---
PYTHON_CMD="python3"
if [[ -d ".venv" ]]; then
    echo "Local Python virtual environment '.venv' found. Using it."
    PYTHON_CMD=".venv/bin/python3"
    if [[ ! -x "$PYTHON_CMD" ]]; then
        echo "Error: .venv/bin/python3 not found or not executable." >&2
        exit 1
    fi
fi
# --- End of venv detection ---

MODE="live"
# CERT_MODE controls the appearance of the certificate ("live" or "dry")
CERT_MODE="live"
DEVICE=""

# --- CORRECT, ROBUST ARGUMENT PARSING ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry)
            MODE="dry"       # Do not execute wipe commands
            CERT_MODE="dry"  # Generate a certificate with a "DRY RUN" banner
            shift
            ;;
        --simulate)
            MODE="dry"       # Do not execute wipe commands
            CERT_MODE="live" # But generate a certificate that looks authentic
            shift
            ;;
        --live)
            MODE="live"      # Execute all commands
            CERT_MODE="live" # Generate an authentic certificate
            shift
            ;;
        -*)
            echo "Unknown flag: $1"
            echo "Usage: $0 [--dry|--simulate|--live] /dev/DEVICE"
            exit 1
            ;;
        *)
            if [[ -n "$DEVICE" ]]; then
                echo "Error: Multiple devices specified. Already have '$DEVICE', found '$1'."
                exit 1
            fi
            DEVICE="$1"
            shift
            ;;
    esac
done

if [[ -z "$DEVICE" ]]; then
    echo "Error: Device not specified."
    echo "Usage: $0 [--dry|--simulate|--live] /dev/DEVICE"
    exit 1
fi

# In live mode, device must be a block device. In dry/simulate, we can be more lenient.
if [[ "$MODE" == "live" && ! -b "$DEVICE" ]]; then
    echo "Error: In live mode, '$DEVICE' must be a valid block device."
    exit 1
fi

echo "Execution Mode: $MODE (Certificate Mode: $CERT_MODE)"
echo "Detected device: $DEVICE"
lsblk -o NAME,SIZE,MODEL,TYPE,SERIAL,MOUNTPOINT "$DEVICE" || true

# --- Confirm ---
read -p "Type YES to confirm you want to proceed with device '$DEVICE': " CONF
CONF=$(echo "$CONF" | tr '[:lower:]' '[:upper:]')
if [[ "$CONF" != "YES" ]]; then
  echo "Aborting"; exit 1
fi

# --- Run wrapper ---
# This function is only controlled by $MODE. It prevents destructive commands.
run_cmd() {
    if [[ "$MODE" == "dry" ]]; then
        printf "[DRY] %s\n" "$*"
    else
        "$@"
    fi
}

# --- Wipe Logic ---
WIPE_METHOD=""
if [[ "$(basename "$DEVICE")" =~ ^nvme ]]; then
    WIPE_METHOD="NVMe Format (Cryptographic Erase, SES=1)"
    run_cmd nvme format "$DEVICE" -s 1
else
    if command -v hdparm >/dev/null; then
        WIPE_METHOD="hdparm ATA Secure Erase"
        run_cmd hdparm --user-master u --security-set-pass PASS "$DEVICE"
        run_cmd hdparm --user-master u --security-erase PASS "$DEVICE"
    else
        WIPE_METHOD="shred (3 passes, pseudorandom)"
        run_cmd shred -v -n 3 "$DEVICE"
    fi
fi

# --- Verify wipe sample ---
echo "After-wipe verification sample:"
VERIFICATION_HASH=""

# If CERT_MODE is 'dry', we use a placeholder.
# Otherwise (for --simulate and --live), we perform the REAL read operation.
if [[ "$CERT_MODE" == "dry" ]]; then
    VERIFICATION_HASH="<not-run-in-dry-mode>"
    echo "[DRY] Hash: $VERIFICATION_HASH"
else
    echo "Reading first 4K of device to generate hash..."
    # This dd command is read-only and safe to run in --simulate mode
    VERIFICATION_HASH=$(dd if="$DEVICE" bs=4096 count=1 2>/dev/null | sha256sum | awk '{print $1}')
    echo "Hash: $VERIFICATION_HASH"
fi

# --- Generate wipe certificate ---
CERT_FILENAME_BASE="wipe_$(basename "$DEVICE")_$(date +%Y%m%d_%H%M%S)"
echo "Generating wipe certificate..."

# Pre-flight dependency check
if ! "$PYTHON_CMD" -c "import weasyprint" &>/dev/null; then
    echo "ERROR: Python dependency 'WeasyPrint' is not installed." >&2
    exit 1
fi
if [[ ! -f ./gen_cert.py ]]; then
    echo "Error: gen_cert.py not found in the current directory."
    exit 1
fi

# We pass $CERT_MODE to the python script, which controls the banner
chmod +x ./gen_cert.py
"$PYTHON_CMD" ./gen_cert.py "$DEVICE" "$CERT_FILENAME_BASE" "$WIPE_METHOD" "$VERIFICATION_HASH" "$CERT_MODE"
