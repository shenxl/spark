pid=$(cat /var/run/mybot.pid)
if [ -n "$pid" ]; then
    kill -HUP $pid
fi