#!/bin/bash

### BEGIN INIT INFO
# Provides:          graylog2-server
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:
# Default-Stop:      0 1 6
# Short-Description: Starts graylog2-server
# Description: This daemon listens for syslog and GELF messages and stores them in mongodb
# chkconfig: - 80 15
### END INIT INFO

[ -f /etc/rc.d/init.d/functions ] && . /etc/rc.d/init.d/functions

#####################
## Any changes to settings make in /etc/sysconfig/graylog2-server
#####################
JAVA_CMD=`which java 2>/dev/null`

GRAYLOG2_SERVER_CTL_DIR=/usr/local/graylog2/server
GRAYLOG2_SERVER_JAR=/usr/local/graylog2/server/graylog2-server.jar
GRAYLOG2_SERVER_CONF=/etc/graylog2/server.conf
GRAYLOG2_SERVER_LOG_CONF=/etc/graylog2/log4j-server.xml
GRAYLOG2_SERVER_PID=/var/run/graylog2/server.pid
GRAYLOG2_USER=graylog2

ADDITIONAL_JAVA_OPTS="-Xms256m -Xmx1g"
#####################
## End changes
#####################

[ -f /etc/sysconfig/graylog2-server ] && . /etc/sysconfig/graylog2-server

RETVAL=0

# Make sure that the java exec is found

if [[ "" =~ "$JAVA_CMD" || ! -x $JAVA_CMD ]] ; then
	echo "ERROR: Java not found! Exiting."
	echo_failure
	$RETVAL=1
	exit 1
fi

start() {
    echo -n "Starting graylog2-server ..."
    cd "$GRAYLOG2_SERVER_CTL_DIR/.."

    if [[ -f ${GRAYLOG2_SERVER_LOG_CONF} ]]
    then
        ADDITIONAL_JAVA_OPTS="${ADDITIONAL_JAVA_OPTS} -Dlog4j.configuration=file://${GRAYLOG2_SERVER_LOG_CONF}"
    fi

    su -s /bin/sh ${GRAYLOG2_USER} -c "${JAVA_CMD} ${ADDITIONAL_JAVA_OPTS} -jar \
                                       ${GRAYLOG2_SERVER_JAR} \
                                       -f ${GRAYLOG2_SERVER_CONF} \
                                       -p ${GRAYLOG2_SERVER_PID} >> /dev/null 2>&1 &"
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
    PID=`cat ${GRAYLOG2_SERVER_PID}`
    echo -n "Stopping graylog2-server ($PID) ..."
    if kill $PID; then
        rm ${GRAYLOG2_SERVER_PID}
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
            echo "graylog2-server running as pid $pid"
            return 0
        else
            echo "Stale pid file with $pid - removing..."
            rm ${GRAYLOG2_SERVER_PID}
        fi
    fi

    echo "graylog2-server not running"
    return 3
}

configtest() {
    echo -n "Validating graylog2-server configuration..."

    if [[ ! -f ${GRAYLOG2_SERVER_LOG_CONF} ]]
    then
        echo
        echo "Logging configuration file set but file doesn't exist, exiting... "
        echo_failure
        echo
        exit 1
    fi

    xmllint --noout ${GRAYLOG2_SERVER_LOG_CONF} >> /dev/null 2>&1
    if [[ $? -ne 0 ]]
    then
        echo
        echo "Syntax errors detected in ${GRAYLOG2_SERVER_LOG_CONF}, run 'xmllint' to debug"
        echo_failure
        echo
        exit 2
    fi

    java_opts="-Dlog4j.configuration=file://${GRAYLOG2_SERVER_LOG_CONF}"
    ${JAVA_CMD} ${java_opts} \
        -jar ${GRAYLOG2_SERVER_JAR} \
        -f ${GRAYLOG2_SERVER_CONF} \
        --configtest

    if [ $? -eq 0 ]
    then
        echo_success
    else
        echo_failure
    fi

    echo
}

get_pid() {
    cat ${GRAYLOG2_SERVER_PID} 2> /dev/null
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
