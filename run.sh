#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

is_mobile_runtime() {
    if [ "${NF_MOBILE_MODE:-}" = "1" ]; then
        return 0
    fi

    if [ -n "${TERMUX_VERSION:-}" ]; then
        return 0
    fi

    if [ -n "${ANDROID_ROOT:-}" ] && [ -n "${ANDROID_DATA:-}" ]; then
        return 0
    fi

    case "${PREFIX:-}" in
        /data/data/*|*/com.termux/*)
            return 0
            ;;
    esac

    return 1
}

find_system_python() {
    if command -v python3 >/dev/null 2>&1; then
        command -v python3
        return 0
    fi

    if command -v python >/dev/null 2>&1; then
        command -v python
        return 0
    fi

    echo "Python tidak ditemukan. Install Python dulu lalu jalankan lagi." >&2
    return 1
}

if is_mobile_runtime; then
    PYTHON_BIN=$(find_system_python)
    export NF_MOBILE_MODE=1

    if ! "$PYTHON_BIN" -c "import requests, urllib3" >/dev/null 2>&1; then
        echo "Menyiapkan dependency HP: requests urllib3"
        "$PYTHON_BIN" -m pip install requests urllib3
    fi

    exec "$PYTHON_BIN" "$SCRIPT_DIR/nf-token-generator.py" "$@"
fi

if [ ! -x "$SCRIPT_DIR/myenv/bin/python" ]; then
    PYTHON_BIN=$(find_system_python)
    echo "Membuat virtualenv: myenv"
    if ! "$PYTHON_BIN" -m venv "$SCRIPT_DIR/myenv"; then
        echo "Gagal membuat myenv. Pastikan modul venv tersedia untuk Python." >&2
        exit 1
    fi
fi

PYTHON_BIN="$SCRIPT_DIR/myenv/bin/python"

if ! "$PYTHON_BIN" -c "import requests, urllib3, playwright" >/dev/null 2>&1; then
    echo "Menyiapkan dependency desktop: requests urllib3 playwright"
    "$PYTHON_BIN" -m pip install requests urllib3 playwright
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/nf-token-generator.py" "$@"
