
#!/bin/bash
# It gets the list of urls as input 
# The condition in if statement determines the
# number of videos we are going to use
filename=$1
n=1
while read line; do
# reading each line
echo "Video URL is : $line"
n=$((n+1))
if [[ $n -gt 114 ]]
then
     break
else
    # can use salt -N group name etc
    salt -L 'raspi-e4:5f:01:72:9e:28' cmd.run 'python3.10 pinot_minion_tasks/example.py '$line' 120 full_video' &
fi
done < $filename
