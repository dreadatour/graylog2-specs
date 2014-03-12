#!/bin/bash

### BEGIN INIT INFO
# Provides:          graylog2-web-interface
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:
# Default-Stop:      0 1 6
# Short-Description: Web interface for the graylog2 message collector
# Description:       This daemon provides a front-end web interface for the Graylog2 message collector
# chkconfig: - 80 15
### END INIT INFO

[ -f /etc/rc.d/init.d/functions ] && . /etc/rc.d/init.d/functions

#####################
## Any changes to settings make in /etc/sysconfig/graylog2-web-interface
#####################
JAVA_CMD=`which java 2>/dev/null`

GRAYLOG2_WEB_CTL_DIR=/usr/local/graylog2/web-interface
GRAYLOG2_WEB_CLASSPATH="/usr/local/graylog2/web-interface/lib/*"
GRAYLOG2_WEB_CONF=/etc/graylog2/web-interface.conf
GRAYLOG2_WEB_LOG_CONF=/etc/graylog2/log4j-web-interface.xml
GRAYLOG2_WEB_PID=/var/run/graylog2/web-interface.pid
GRAYLOG2_USER=graylog2

ADDITIONAL_JAVA_OPTS="-XX:ReservedCodeCacheSize=128m"
MIN_MEM=1024m
MAX_MEM=1024m
MAX_PERM_SIZE=256m
#####################
## End changes
#####################

[ -f /etc/sysconfig/graylog2-web-interface ] && . /etc/sysconfig/graylog2-web-interface

RETVAL=0

# Make sure that the java exec is found

if [[ "" =~ "$JAVA_CMD" || ! -x $JAVA_CMD ]] ; then
    echo "ERROR: Java not found! Exiting."
    echo_failure
    $RETVAL=1
    exit 1
fi

start() {
    echo -n "Starting graylog2-web-interface ..."
    cd "$GRAYLOG2_WEB_CTL_DIR/"

    if [[ -f ${GRAYLOG2_WEB_CONF} ]]; then
        ADDITIONAL_JAVA_OPTS="${ADDITIONAL_JAVA_OPTS} -Dconfig.file=${GRAYLOG2_WEB_CONF}"
    fi

    if [[ -f ${GRAYLOG2_WEB_LOG_CONF} ]]; then
        ADDITIONAL_JAVA_OPTS="${ADDITIONAL_JAVA_OPTS} -Dlogger.file=${GRAYLOG2_WEB_LOG_CONF}"
    fi

    su -s /bin/sh $GRAYLOG2_USER -c "${JAVA_CMD} -Xms${MIN_MEM} -Xmx${MAX_MEM} \
                                     -XX:MaxPermSize=${MAX_PERM_SIZE} ${ADDITIONAL_JAVA_OPTS} \
                                     -Duser.dir=${GRAYLOG2_WEB_CTL_DIR} \
                                     -Dpidfile.path=${GRAYLOG2_WEB_PID} \
                                     -cp \"$GRAYLOG2_WEB_CLASSPATH\" play.core.server.NettyServer >> /dev/null 2>&1 &"
    RETVAL=$?

    if [ $RETVAL -eq 0 ]
    then
        echo_success
    else
        echo_failure
    fi

    echo
}

stop() {
    PID=$(get_pid)
    echo -n "Stopping graylog2-web-interface ($PID) ..."
    if kill $PID; then
        rm ${GRAYLOG2_WEB_PID}
        echo_success
    else
        echo_failure
    fi
    echo
}

restart() {
    stop
    sleep 5
    start
}

status() {
    pid=$(get_pid)
    if [ ! -z $pid ]; then
        if pid_running $pid; then
            echo "graylog2-web-interface running as pid $pid"
            return 0
        else
            echo "Stale pid file with $pid - removing..."
            rm ${GRAYLOG2_WEB_PID}
        fi
    fi

    echo "graylog2-web-interface not running"
    return 3
}

configtest() {
    echo -n "Validating graylog2-web-interface configuration..."

    if [[ ! -f ${GRAYLOG2_WEB_LOG_CONF} ]]
    then
        echo
        echo "Logging configuration file set but file doesn't exist, exiting... "
        echo_failure
        echo
        exit 1
    fi

    xmllint --noout ${GRAYLOG2_WEB_LOG_CONF} >> /dev/null 2>&1
    if [[ $? -ne 0 ]]
    then
        echo
        echo "Syntax errors detected in ${GRAYLOG2_WEB_LOG_CONF}, run 'xmllint' to debug"
        echo_failure
        echo
        exit 2
    fi

    echo_success

    echo
}

get_pid() {
    cat ${GRAYLOG2_WEB_PID} 2> /dev/null
}

pid_running() {
    kill -0 $1 2> /dev/null
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    configtest)
        configtest
        ;;
    *)
        echo "Usage $0 {start|stop|restart|status|configtest}"
        RETVAL=1
esac
