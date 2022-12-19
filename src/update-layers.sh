#!/bin/bash
clear

PY_PATH=/usr/smb-share/de-result/venv/bin/python3
cd /usr/smb-share/de-result/src
$PY_PATH 1_log_parser.py && $PY_PATH 2_users_call.py && $PY_PATH 2_db_call.py && $PY_PATH 2_app_call.py
$PY_PATH source_clear.py
