%define __prefix /usr/local

Name:           graylog2-radio
Summary:        A message receiver front-end to expand on a graylog2 network
Version:        0.20.0
Release:        1%{?dist}
License:        GPL 3.0
Group:          MAILRU
Prefix:         %{_prefix}

Url:            http://graylog2.org/
Source0:        https://github.com/Graylog2/graylog2-server/releases/download/%{version}/%{name}-%{version}.tgz
Source1:        graylog2-radio-config
Source2:        graylog2-radio-init.d
Source3:        graylog2-radio-sysconfig
Source4:        graylog2-radio-log4j.xml
Source5:        graylog2-radio-logrotate.d
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       graylog2-server
Requires:       libxml2
Requires:       java-1.7.0-openjdk

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils


%description

The graylog2-radio package is an expasion package in the Graylog2 family of
packages. It works by accepting messages from inputs, converting them into
an internal Graylog2 message format and writes them to a Kafka cluster.
From there one or more graylog2-server nodes can process the messages, run
all extractors and/or converters and write them to configured output(s).

This package is optional, but can be useful if your environments endure
exteremly high message throughput rates. Having radio nodes may significantly
reduce the load on your graylog2-server node(s)


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
%{__install} -p %{SOURCE1} %{buildroot}%{_sysconfdir}/graylog2/radio.conf
%{__install} -p %{SOURCE4} %{buildroot}%{_sysconfdir}/graylog2/log4j-radio.xml

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
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/radio
%{__install} -p -m 644 graylog2-radio.jar %{buildroot}%{__prefix}/graylog2/radio/


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
%config(noreplace) %{_sysconfdir}/graylog2/radio.conf
%config(noreplace) %{_sysconfdir}/graylog2/log4j-radio.xml

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
%{__prefix}/graylog2/radio/*
