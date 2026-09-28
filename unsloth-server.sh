#!/bin/bash
filtered_args=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --spec-default)
            shift
            ;;
        --fit)
            if [[ "$2" == "on" || "$2" == "off" ]]; then
                shift 2
            fi
            ;;
        *)
            filtered_args+=("$1")
            shift
            ;;
    esac
done

ik_llama.cpp/build/bin/llama-server.orig \ 
"${filtered_args[@]}"
