#!/bin/bash
SERVICE="luigi"
if pgrep -x "$SERVICE" > /dev/null
then exit 1
else exit 0
fi
