#!/bin/bash
function log() {
    local level=$1
    local message=$2
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Create JSON formatted log using jq to handle escaping
    local log_data=$(jq -n \
        --arg ts "$timestamp" \
        --arg name "benchify.sh" \
        --arg lvl "$level" \
        --arg msg "$message" \
        '{timestamp: $ts, name: $name, level: $lvl, message: $msg}')
    
    # Get console logging level from environment variable, default to HIGH
    console_level=${LOG_CONSOLE_LEVEL:-HIGH}
    
    # Map log levels to numeric values for comparison
    declare -A level_values=(
        ["LOW"]=10
        ["MEDIUM"]=20
        ["HIGH"]=30
        ["SEVERE"]=40
        ["CRITICAL"]=50
    )
    
    # Map input level to numeric value for comparison
    declare -A input_values=(
        ["INFO"]=20
        ["DEBUG"]=10
        ["WARNING"]=30
        ["ERROR"]=40
        ["CRITICAL"]=50
    )
    
    # Only print if input level >= console level
    if [ "${input_values[$level]:-0}" -ge "${level_values[$console_level]:-30}" ]; then
        echo "$log_data"
    fi
}

# Check if argument is provided
if [ $# -ne 1 ]; then
    log "ERROR" "Please provide Root dir as argument"
    exit 1
fi

ROOT_PATH=$1
BENCHIFY_CONFIG_DIR=$ROOT_PATH/repo/.benchify
benchify_config_path="$BENCHIFY_CONFIG_DIR/benchify.json"

# ╔═══════════════════════════╗
# ║         PYTHON            ║
# ╚═══════════════════════════╝

# Load Python version from file
if [ -f "$benchify_config_path" ]; then
    # Read the existing benchify.json content
    benchify_config=$(cat "$benchify_config_path")

    # Extract the Python version from the JSON content
    pythonVersion=$(echo "$benchify_config" | jq -r '.languages.python.version' | cut -d '.' -f 2)

    log "INFO" "Loaded Python version from benchify.json: 3.$pythonVersion"
else
    log "ERROR" "benchify.json not found at $benchify_config_path"
fi

pythonVersion=${pythonVersion:-"null"}

# TODO: Temporary solution to avoid setting up python environment for TS projects.
if [ "$pythonVersion" != "null" ]; then
    # Create virtual environment path
    venv_path="$ROOT_PATH/venv3.$pythonVersion"

    # Check if virtual environment exists
    if [ ! -d "$venv_path" ]; then
        echo "Error: Virtual environment not found at $venv_path"
    fi

    # Check if Python executable exists
    if [ ! -f "$venv_path/bin/python" ]; then
        echo "Error: Python executable not found in virtual environment"
    fi

    # Source the .env.benchify.python file
    if [ -f "$BENCHIFY_CONFIG_DIR/.env.benchify.python" ]; then
        log "INFO" "Sourcing environment variables from .env.benchify.python"
        set -o allexport
        source "$BENCHIFY_CONFIG_DIR/.env.benchify.python"
        set +o allexport
    else
        log "ERROR" ".env.benchify.python not found at $BENCHIFY_CONFIG_DIR"
    fi
fi


# ╔═══════════════════════════════╗
# ║         TYPESCRIPT            ║
# ╚═══════════════════════════════╝

# Source the .env.benchify.typescript file
if [ -f "$BENCHIFY_CONFIG_DIR/.env.benchify.typescript" ]; then
    log "INFO" "Sourcing environment variables from .env.benchify.typescript"
    set -o allexport
    source "$BENCHIFY_CONFIG_DIR/.env.benchify.typescript"
    set +o allexport
else
    log "INFO" ".env.benchify.typescript not found at $BENCHIFY_CONFIG_DIR"
fi

# Copy $BENCHIFY_CONFIG_DIR/tsconfig.json to repo/tsconfig.json
if [ -f "$BENCHIFY_CONFIG_DIR/tsconfig.json" ]; then
    cp "$BENCHIFY_CONFIG_DIR/tsconfig.json" "repo/tsconfig.json"
    log "INFO" "Copied tsconfig.json to repo/tsconfig.json"
else
    log "INFO" "tsconfig.json not found at $BENCHIFY_CONFIG_DIR"
fi

# Do not edit above commands

# TODO: record only non failing commands, atm all commands are recorded, or maybe we should record all commands anyway to give customers a better foundation for debugging?
pipreqs $ROOT_PATH/repo --mode no-pin --force --savepath $ROOT_PATH/repo/requirements.txt
$venv_path/bin/python -m pip install -r $ROOT_PATH/repo/requirements.txt --prefer-binary --disable-pip-version-check --no-compile
/root/.bun/bin/bun install --no-progress
