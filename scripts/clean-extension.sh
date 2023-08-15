#!/bin/bash

# Verificar que se haya proporcionado una cadena como argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <cadena> ('dat', 'xy')"
    exit 1
fi

ext=$1

for d in $(find -maxdepth 2 -type d); do
    cd ${d}
    narchs=$(ls *.${ext} 2>/dev/null | wc -l)
    if [ ${narchs} -gt 0 ]; then
        echo "Cantidad de archivos en " ${d} : ${narchs}
        echo "Borrando archivos *.'${ext}'  ..."
        rm -rf *.${ext}
        echo "Directorio '${d}'" limpio.
    fi
    cd - &>/dev/null
done
echo "Proceso completado."
