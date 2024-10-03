#!/bin/bash

# Verificação de Argumentos
if [ $# -ne 1 ]; then
    echo "Modo de uso: $0 <número de instâncias>"
    exit 1
fi

NUM_INSTANCES=$1

SCRIPT="client.py"

for i in $(seq 1 $NUM_INSTANCES); do
    echo "Começando instância $i..."
    python3 $SCRIPT &
    sleep 0.5
done

wait

echo "Tudo Finalizado."
