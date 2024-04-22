#!/bin/ksh
# Loop 10000 times for 230,000 hands
rm play_poker.txt 2>/dev/null
for ((ctr=1; ctr<=10000; ctr++))
do
    ./deal_hands.py >> play_poker.txt
done
