Graylog2 SPECS for CentOS
=========================

All that you need to build CentOS RPMs for:

* [GrayLog2 Server][graylog2-server] 0.20.1
* [GrayLog2 Radio][graylog2-radio] 0.20.0
* [GrayLog2 Web Interface][graylog2-web-interface] 0.20.1
* [ElasticSearch][elasticsearch] 0.90.10
* [Logstash][logstash] 1.3.3
* [Logstash-forwarder][logstash-forwarder] 0.3.1


Set Up an RPM Build Environment under CentOS
--------------------------------------------

More info: [Set Up an RPM Build Environment][prepare-rpm].

    yum install rpm-build make gcc
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros

Another way:

    yum install rpmdevtools
    rpmdev-setuptree


Prepare
-------

    mkdir ~/temp
    cd ~/temp/
    git clone https://github.com/dreadatour/graylog-specs.git
    cp -vr graylog-specs/* ~/rpmbuild/
    cd ~/rpmbuild/


Build GrayLog2 Server RPM
-------------------------

    rpmbuild -v -bb SPECS/graylog2-server.spec

Result RPM:

    ls ~/rpmbuild/RPMS/x86_64/graylog2-server-0.20.1-1.el6.x86_64.rpm


Build GrayLog2 Radio RPM
------------------------

    rpmbuild -v -bb SPECS/graylog2-radio.spec

Result RPM:

    ls ~/rpmbuild/RPMS/x86_64/graylog2-radio-0.20.0-1.el6.x86_64.rpm


Build GrayLog2 Web Interface RPM
------------------------

    rpmbuild -v -bb SPECS/graylog2-web-interface.spec

Result RPM:

    ls ~/rpmbuild/RPMS/x86_64/graylog2-web-interface-0.20.1-1.el6.x86_64.rpm


Build ElasticSearch RPM
-----------------------

    rpmbuild -v -bb SPECS/elasticsearch.spec

Result RPM:

    ls ~/rpmbuild/RPMS/x86_64/elasticsearch-0.90.10-1.el6.x86_64.rpm


Build Logstash RPM
------------------

    rpmbuild -v -bb SPECS/logstash.spec

Result RPM:

    ls ~/rpmbuild/RPMS/x86_64/logstash-1.3.3-1.el6.x86_64.rpm


Build Logstash-forwarder RPM
----------------------------

    rpmbuild -v -bb SPECS/logstash-forwarder.spec

Result RPM:

    ls ~/rpmbuild/RPMS/x86_64/logstash-forwarder-0.3.1-1.el6.x86_64.rpm


[graylog2-server]: http://graylog2.org/
[graylog2-radio]: http://support.torch.sh/help/kb/graylog2-server/using-graylog2-radio-v020x
[graylog2-web-interface]: https://github.com/Graylog2/graylog2-web-interface
[elasticsearch]: http://www.elasticsearch.com/
[logstash]: https://http://logstash.net/
[logstash-forwarder]: https://github.com/elasticsearch/logstash-forwarder
[prepare-rpm]: http://wiki.centos.org/HowTos/SetupRpmBuildEnvironment
