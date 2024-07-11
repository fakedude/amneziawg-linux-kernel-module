#!/bin/bash

AWG_TEMP_DIR="$(cat /var/lib/amnezia/amneziawg/.tempdir 2>/dev/null)"
PREFIX=${AWG_TEMP_DIR:-/tmp}
WORKDIR="${PREFIX}/amneziawg"

[ -e kernel ] && rm -f kernel
[ -d "${WORKDIR}" ] && rm -rf "${WORKDIR}"