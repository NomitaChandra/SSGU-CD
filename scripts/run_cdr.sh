#!/bin/sh

python train_pubtator_2.py --task cdr --use_gcn mentions --demo false --seed 66

sleep 100

python train_pubtator_2.py --task cdr --use_gcn tree --demo false --seed 66

sleep 100

python train_pubtator_2.py --task cdr --use_gcn mentions --demo false --seed 68

sleep 100

python train_pubtator_2.py --task cdr --use_gcn tree --demo false --seed 68

sleep 100

python train_pubtator_2.py --task cdr --use_gcn mentions --demo false --seed 70

sleep 100

python train_pubtator_2.py --task cdr --use_gcn tree --demo false --seed 70

sleep 100

python train_pubtator_2.py --task cdr --use_gcn false --demo false --seed 66

sleep 100

python train_pubtator_2.py --task cdr --use_gcn false --demo false --seed 68