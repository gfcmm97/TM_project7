#!/bin/bash
cd "$(dirname "$0")"
source back/.venv/bin/activate
gnome-terminal -- bash -c "cd back && uvicorn main:app --reload; exec bash"
xdg-open front/main.html || open front/main.html
