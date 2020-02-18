#!/usr/bin/env bash

#
# Is sshfs running? 
#

if mount | grep osxfuse > /dev/null; then
	echo '✔️'
    echo '---'
else
	echo '❌'
    echo '---'
fi
