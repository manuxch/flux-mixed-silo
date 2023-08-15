#!/bin/bash

# Verificar que se haya proporcionado una cadena como argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <cadena> ('q6-ve', 'frames', 'flx', 'fms', 'params')"
    exit 1
fi

pref=$1

for d in $(find -maxdepth 2 -type d); do
    cd ${d}
    for f in $(ls *); do
        if [ -f ${f} ] && [[ "$( basename ${f})" == ${pref}* ]]; then
            echo "Descomprimiendo '${f}'" en ${d}
            7z e ${f}
        fi
    done
    cd - &>/dev/null
done
echo "Proceso completado."
