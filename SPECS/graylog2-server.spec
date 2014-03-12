%define __prefix /usr/local

Name:           graylog2-server
Summary:        A syslog receiver and processing system
Version:        0.20.1
Release:        1%{?dist}
License:        GPL 3.0
Group:          MAILRU
Prefix:         %{_prefix}

Url:            http://graylog2.org/
Source0:        https://github.com/Graylog2/%{name}/releases/download/%{version}/%{name}-%{version}.tgz
Source1:        graylog2-server-config
Source2:        graylog2-server-init.d
Source3:        graylog2-server-sysconfig
Source4:        graylog2-server-log4j.xml
Source5:        graylog2-server-logrotate.d
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       mongodb-server
Requires:       elasticsearch
Requires:       libxml2
Requires:       java-1.7.0-openjdk

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils


%description

A syslog processing system that stores received messages in an Elasticsearch database. When coupled with
the graylog2-web-interface, which provides a front-end web interface, will allow for powerful message
analytics for a server network.

Other information, including but not limited to user credentials, stream configurations, etc, are stored
in MongoDB


%prep
%setup -q -n %{name}-%{version}


%build
true


%install
rm -rf %{buildroot}

# Config
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -p %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%{__mkdir} -p %{buildroot}%{_sysconfdir}/graylog2
%{__install} -p %{SOURCE1} %{buildroot}%{_sysconfdir}/graylog2/server.conf
%{__install} -p %{SOURCE4} %{buildroot}%{_sysconfdir}/graylog2/log4j-server.xml

# INIT scripts
%{__mkdir} -p %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -p -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}

# Logs and Run
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/graylog2
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/graylog2

# Logrotate
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d/
%{__install} -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install Root
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/server
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/server/plugin
%{__install} -p -m 644 graylog2-server.jar %{buildroot}%{__prefix}/graylog2/server/
cp -pR plugin/* %{buildroot}%{__prefix}/graylog2/server/plugin/


%pre
# create graylog2 group
if ! getent group graylog2 >/dev/null; then
    groupadd -r graylog2
fi

# create graylog2 user
if ! getent passwd graylog2 >/dev/null; then
    useradd -r -g graylog2 -d %{__prefix}/graylog2 -s /sbin/nologin -c "You know, for logs" graylog2
fi


%post
/sbin/chkconfig --add %{name}


%preun
if [ $1 -eq 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}
fi


%clean
#rm -rf %{buildroot}


%files
%defattr(-,root,root,-)

# Configurations
%config(noreplace) %{_sysconfdir}/graylog2/server.conf
%config(noreplace) %{_sysconfdir}/graylog2/log4j-server.xml

# Logrotate
%{_sysconfdir}/logrotate.d/%{name}

# Sysconfig and Init
%dir %{_sysconfdir}/sysconfig
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%dir %{_sysconfdir}/rc.d/init.d
%attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/%{name}

%defattr(-,graylog2,graylog2,-)

# Logs and Run
%dir %{_localstatedir}/run/graylog2
%dir %{_localstatedir}/log/graylog2

# Install root
%dir %{__prefix}/graylog2
%{__prefix}/graylog2/server/*
