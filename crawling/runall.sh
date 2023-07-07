#!/bin/bash

# list of python scripts
scripts=("./autohome/autohome.py" "./dcd/dcd.py" "./toutiao/toutiao.py" "./xhs/xhs.py" "./yiche/yiche.py")

# run scripts in background
for script in "${scripts[@]}"
do
    python "$script" &
done

# wait for all background jobs to finish
wait

echo "All scripts have finished running."