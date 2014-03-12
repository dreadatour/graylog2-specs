#!/bin/sh

# Taken from https://github.com/piojo/logstash-rpm/blob/lsb/SOURCES/logstash.wrapper
SCRIPT=$0

if [ -x "$JAVA_HOME/bin/java" ]; then
    JAVA=$JAVA_HOME/bin/java
else
    JAVA=`which java`
fi

LOGSTASH_JAR="/usr/local/logstash/lib/logstash.jar"
if [ ! -f $LOGSTASH_JAR ]; then
    echo "jar file is not found."
    exit 99
fi

if [ "x$LOGSTASH_MIN_MEM" = "x" ]; then
    LOGSTASH_MIN_MEM=256m
fi
if [ "x$LOGSTASH_MAX_MEM" = "x" ]; then
    LOGSTASH_MAX_MEM=1g
fi
if [ "x$LOGSTASH_HEAP_SIZE" != "x" ]; then
    LOGSTASH_MIN_MEM=$LOGSTASH_HEAP_SIZE
    LOGSTASH_MAX_MEM=$LOGSTASH_HEAP_SIZE
fi

# min and max heap sizes should be set to the same value to avoid
# stop-the-world GC pauses during resize, and so that we can lock the
# heap in memory on startup to prevent any of it from being swapped
# out.
JAVA_OPTS="$JAVA_OPTS -Xms${LOGSTASH_MIN_MEM}"
JAVA_OPTS="$JAVA_OPTS -Xmx${LOGSTASH_MAX_MEM}"

function usage() {
    echo "Usage: ${SCRIPT} OPTIONS"
    echo "  OPTIONS:"
    echo -e "    -f, --config CONFIGFILE (required)  Load the Logstash config from a specific file or directory."
    echo -e "                                        If a directory is given instead of a file, all files in that"
    echo -e "                                        directory will be concatenated in lexicographical order and then"
    echo -e "                                        parsed as a single config file."
    echo -e "    -p, --pluginpath PLUGIN_PATH        A colon-delimited path to find plugins in."
    echo -e "    -P, --pidfile PIDFILE               PID file path."
    echo -e "    -l, --logfile LOGFILE               Logfile path. Providing this will automatically run Logstash in the background"
    echo -e "    -v, --log-level LEVEL               Changes log level. Options: error, warn, info, debug (default: warn)"
    echo -e "    -w, --filterworkers                 Sets number of filterworkers."
}

function run() {
    config=$1
    pluginpath=$2
    pidfile=$3
    logfile=$4
    loglevel=$5
    workers=$6

    if [ "x$config" == "x" ]; then
        echo "ERROR: config file is required."
        usage
        exit 1
    fi

    if [ "x$logfile" == "x" ]; then
        exec "$JAVA" $JAVA_OPTS -jar $LOGSTASH_JAR agent $loglevel -f "$config" -p "$pluginpath" -w "$workers"
        rs=$?
    else
        exec "$JAVA" $JAVA_OPTS -jar $LOGSTASH_JAR agent $loglevel -f "$config" -l "$logfile" -p "$pluginpath" -w "$workers" >> $logfile 2>&1 &
        rs=$?
        [ $rs -eq 0 -a "x$pidfile" != "x" ] && printf '%d' $! > "$pidfile"
    fi

    return $rs
}

while test $# -gt 0
do
    case "$1" in
        -V | --version)
            "$JAVA" -jar $LOGSTASH_JAR --version
            exit 0
        ;;

        -f | --config)
            config="$2"
            if [ ! -f "$config" -a ! -d "$config" ]; then
                echo "ERROR: config file or directory \`$config' does not exist."
                usage
                exit 1
            fi
            shift 2
        ;;

        -p | --pluginpath)
            pluginpath="$2"
            if [ ! -d "$pluginpath" ]; then
                echo "ERROR: config directory \`$pluginpath' does not exist."
                usage
                exit 1
            fi
            shift 2
        ;;

        -P | --pidfile)
            pidfile="$2"
            shift 2
        ;;

        -l | --logfile)
            logfile="$2"
            shift 2
        ;;

        -v | --log-level)
            if [ "$2" == "error" ]; then
                loglevel="--quiet"
            elif [ "$2" == "debug" ]; then
                loglevel="--debug"
            elif [ "$2" == "info" ]; then
                loglevel="--verbose"
            fi
            shift 2
        ;;

        -w | --filterworkers )
            workers="$2"
            shift 2
        ;;

        -h | --help)
            usage
            exit 0
        ;;

        *)
            break
    esac
done

run "$config" "$pluginpath" "$pidfile" "$logfile" "$loglevel" "$workers"

exit $?
