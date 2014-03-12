#!/bin/bash

### BEGIN INIT INFO
# Provides:          logstash
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:
# Default-Stop:      0 1 6
# Short-Description: Starts logstash
# Description: Logstash agent
# chkconfig: - 80 15
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

# Pull in sysconfig settings
[ -f /etc/sysconfig/logstash ] && . /etc/sysconfig/logstash

LOGSTASH_HOME=/usr/local/logstash
LOGSTASH_USER=logstash

DAEMON=${LOGSTASH_HOME}/bin/logstash
PID_FILE=${PIDFILE:-/var/run/logstash/logstash.pid}
LOCK_FILE=${LOCKFILE:-/var/lock/subsys/logstash}
LOG_FILE=${LOGFILE:-/var/log/logstash/logstash.log}

LOGSTASH_PATH_CONF=${LOGSTASH_PATH_CONF:-/etc/logstash/}
LOGSTASH_PATH_PLUGINS=${LOGSTASH_PATH_PLUGINS:-/usr/local/logstash/plugins/}
LOGSTASH_LOGLEVEL=${LOGSTASH_LOGLEVEL:-"warn"}
LOGSTASH_FILTERWORKERS=${LOGSTASH_FILTERWORKERS:-1}

DAEMON_OPTS="-P ${PID_FILE} \
    -p ${LOGSTASH_PATH_PLUGINS} \
    -l ${LOG_FILE} \
    -f ${LOGSTASH_PATH_CONF} \
    -v $LOGSTASH_LOGLEVEL \
    -w $LOGSTASH_FILTERWORKERS"

# These environment variables are passed over.
LOGSTASH_MIN_MEM=${LOGSTASH_MIN_MEM:-256m}
LOGSTASH_MAX_MEM=${LOGSTASH_MAX_MEM:-1g}

start() {
    echo -n $"Starting logstash: "
    export JAVA_OPTS="$JAVA_OPTS$LOGSTASH_JAVA_OPTS"
    daemon --pidfile=${PID_FILE} --user $LOGSTASH_USER \
        LOGSTASH_MIN_MEM=$LOGSTASH_MIN_MEM \
        LOGSTASH_MAX_MEM=$LOGSTASH_MAX_MEM \
        $DAEMON $DAEMON_OPTS
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && touch $LOCK_FILE
    return $RETVAL
}

stop() {
    echo -n $"Stopping logstash: "
    killproc -p ${PID_FILE} -d 10 $DAEMON
    RETVAL=$?
    echo
    [ $RETVAL = 0 ] && rm -f ${LOCK_FILE} ${PID_FILE}
    return $RETVAL
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    status)
        status -p ${PID_FILE} $DAEMON
        RETVAL=$?
    ;;
    restart | force-reload)
        stop
        start
    ;;
    *)
        echo "Usage: /etc/init.d/logstash {start|stop|restart|force-reload}" >&2
        RETVAL=2
    ;;
esac

exit $RETVAL
