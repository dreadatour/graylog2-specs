/var/log/logstash/*.log {
    daily
    rotate 14
    copytruncate
    compress
    missingok
    notifempty
}
