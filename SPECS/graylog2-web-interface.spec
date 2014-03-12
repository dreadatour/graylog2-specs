%define __prefix /usr/local

Name:           graylog2-web-interface
Summary:        A front-end web interface for the Graylog2 syslog receiver
Version:        0.20.1
Release:        1%{?dist}
License:        GPL 3.0
Group:          MAILRU
Prefix:         %{_prefix}

Url:            http://graylog2.org/
Source0:        https://github.com/Graylog2/%{name}/releases/download/%{version}/%{name}-%{version}.tgz
Source1:        https://github.com/Graylog2/graylog2-web-interface/archive/%{version}.zip
Source2:        graylog2-web-interface-config
Source3:        graylog2-web-interface-application.conf
Source4:        graylog2-web-interface-play.plugins
Source5:        graylog2-web-interface-init.d
Source6:        graylog2-web-interface-sysconfig
Source7:        graylog2-web-interface-log4j.xml
Source8:        graylog2-web-interface-logrotate.d
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       graylog2-server
Requires:       libxml2
Requires:       java-1.7.0-openjdk

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils


%description

A front-end web interface for the Graylog2 syslog receiver. This package relies on the configured
REST interfaces of the graylog2-server package and requires almost no other configuration options.


%prep
%setup -q -n %{name}-%{version}
%setup -a 1


%build
true


%install
rm -rf %{buildroot}

# Config
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -p %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%{__mkdir} -p %{buildroot}%{_sysconfdir}/graylog2
%{__install} -p %{SOURCE2} %{buildroot}%{_sysconfdir}/graylog2/web-interface.conf
%{__install} -p %{SOURCE3} %{buildroot}%{_sysconfdir}/graylog2/application.conf
%{__install} -p %{SOURCE4} %{buildroot}%{_sysconfdir}/graylog2/play.plugins
%{__install} -p %{SOURCE7} %{buildroot}%{_sysconfdir}/graylog2/log4j-web-interface.xml

# INIT scripts
%{__mkdir} -p %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -p -m 755 %{SOURCE5} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}

# Logs and Run
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/graylog2
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/graylog2

# Logrotate
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d/
%{__install} -D -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install Root
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/web-interface
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/web-interface/conf
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/web-interface/lib
%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/web-interface/share

%{__mkdir} -p %{buildroot}%{__prefix}/graylog2/web-interface/bin
%{__install} -p -m 755 bin/graylog2-web-interface %{buildroot}%{__prefix}/graylog2/web-interface/bin/

%{__install} -p lib/*.jar %{buildroot}%{__prefix}/graylog2/web-interface/lib

cp -pR share %{buildroot}%{__prefix}/graylog2/web-interface/
cp -pR %{name}-%{version}/public %{buildroot}%{__prefix}/graylog2/web-interface/


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
%config(noreplace) %{_sysconfdir}/graylog2/web-interface.conf
%config(noreplace) %{_sysconfdir}/graylog2/application.conf
%config(noreplace) %{_sysconfdir}/graylog2/play.plugins
%config(noreplace) %{_sysconfdir}/graylog2/log4j-web-interface.xml

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
%{__prefix}/graylog2/web-interface/*
