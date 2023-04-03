pid=$(cat /var/run/mybot.pid)
if [ -n "$pid" ]; then
    kill -9 $pid
fi