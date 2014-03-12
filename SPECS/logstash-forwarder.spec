%define debug_package %{nil}
%define __prefix /usr/local

Name:           logstash-forwarder
Summary:        An experiment to cut logs in preparation for processing elsewhere
Version:        0.3.1
Release:        1%{?dist}
License:        Apache Software License 2.0
Group:          MAILRU
Prefix:         %{_prefix}

Url:            https://github.com/elasticsearch/logstash-forwarder
Source0:        https://github.com/elasticsearch/logstash-forwarder/archive/v%{version}.tar.gz
Source1:        logstash-forwarder-init.d
Source2:        logstash-forwarder-sysconfig
Source3:        logstash-forwarder-config.conf
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  golang

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils


%description
A tool to collect logs locally in preparation for processing elsewhere.


%prep
%setup -q -n %{name}-%{version}


%build
go build


%install
rm -rf $RPM_BUILD_ROOT

%{__mkdir} -p %{buildroot}%{__prefix}/bin
%{__install} -p -m 755  %{_builddir}/%{name}-%{version}/%{name}-%{version} %{buildroot}%{__prefix}/bin/logstash-forwarder

# Config
%{__mkdir} -p %{buildroot}%{_sysconfdir}
%{__install} -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logstash-forwarder.conf

# Misc
%{__mkdir} -p %{buildroot}%{_localstatedir}/run

# sysconfig and init
%{__mkdir} -p %{buildroot}%{_initddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_initddir}/%{name}
%{__install} -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}


%post
/sbin/chkconfig --add %{name}


%preun
if [ $1 -eq 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{__prefix}/bin/logstash-forwarder

# Config
%config(noreplace) %{_sysconfdir}/logstash-forwarder.conf

# Sysconfig and init
%{_initddir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/*
