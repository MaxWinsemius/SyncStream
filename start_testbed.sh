#!/usr/bin/sh

if [[ ! -d "/run/syncstream" ]]; then
    ./boot.sh
fi

own_usr=$(stat -c '%U' /run/syncstream)
own_grp=$(stat -c '%G' /run/syncstream)

if [[ "$own_usr" != "$USER" ]]; then
    sudo chown $USER:$USER /run/syncstream
fi

if [[ "$own_grp" != "$USER" ]]; then
    sudo chown $USER:$USER /run/syncstream
fi

# Now create that tmux testbed session
sesh="syncstream_testbed"
numleds=10

tmux new-session -d -s $sesh
tmux send-keys      -t "$sesh" "./src/terminal_testbed/a.out $numleds 1337" Enter
tmux split-window   -t "$sesh" -dvp80
tmux split-window   -t "$sesh" -hp66
tmux send-keys      -t "$sesh" "./src/terminal_testbed/a.out $numleds 1338" Enter
tmux split-window   -t "$sesh" -h
tmux send-keys      -t "$sesh" "./src/terminal_testbed/a.out $numleds 1339" Enter
tmux select-pane    -t "$sesh" -t "{bottom}"
tmux send-keys      -t "$sesh" "./src/udpserver/udpserver.py ./src/udpserver/terminal_testbed.yaml" Enter
tmux split-window   -t "$sesh" -h -c ./animations
sleep 1
tmux send-keys      -t "$sesh" "ls -1" Enter
tmux send-keys      -t "$sesh" "./src/animations/knight_rider.py" Enter
tmux a
