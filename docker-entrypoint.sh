#!/bin/sh

echo "The application is starting ..."
# Apply environment variables
. /home/techuser/ma4/.env
# Install ma4 project dependency
pip install /home/techuser/ma4
# Run application
exec python3 /home/techuser/ma4/src/ma4/crew_program_gen_youtube_analyze.py "$@"

