%define debug_package %{nil}
%define __prefix /usr/local

Name:           logstash
Summary:        A tool for managing events and logs
Version:        1.3.3
Release:        1%{?dist}
License:        Apache Software License 2.0
Group:          MAILRU
Prefix:         %{_prefix}

Url:            http://logstash.net
Source0:        https://download.elasticsearch.org/logstash/logstash/%{name}-%{version}-flatjar.jar
Source1:        logstash-wrapper.sh
Source2:        logstash-logrotate.d
Source3:        logstash-init.d
Source4:        logstash-sysconfig
Source5:        logstash-config.conf
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       jpackage-utils
Requires:       java-1.7.0-openjdk

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils

%description
A tool for managing events and logs

%prep
true

%build
true

%install
rm -rf $RPM_BUILD_ROOT

# JAR file
%{__mkdir} -p %{buildroot}%{__prefix}/%{name}/lib
%{__install} -p -m 644 %{SOURCE0} %{buildroot}%{__prefix}/%{name}/lib/%{name}.jar

# Config
%{__mkdir} -p %{buildroot}%{_sysconfdir}/%{name}
%{__install} -m 755 %{SOURCE5} %{buildroot}%{_sysconfdir}/%{name}/logstash.conf

# Plugin dir
%{__mkdir} -p %{buildroot}%{__prefix}/%{name}/plugins/logstash/inputs
%{__mkdir} -p %{buildroot}%{__prefix}/%{name}/plugins/logstash/filters
%{__mkdir} -p %{buildroot}%{__prefix}/%{name}/plugins/logstash/outputs
# This is needed because Logstash will complain if there are no *.rb files in its Plugin directory
/bin/echo "Dummy file due to https://logstash.jira.com/browse/LOGSTASH-1555" >  %{buildroot}%{__prefix}/%{name}/plugins/logstash/inputs/dummy.rb

# Wrapper script
%{__mkdir} -p %{buildroot}%{__prefix}/%{name}/bin
%{__install} -m 755 %{SOURCE1} %{buildroot}%{__prefix}/%{name}/bin/%{name}

# Logs
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Misc
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/%{name}

# sysconfig and init
%{__mkdir} -p %{buildroot}%{_initddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE3} %{buildroot}%{_initddir}/%{name}
%{__install} -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# Create Home directory
#   See https://github.com/lfrancke/logstash-rpm/issues/5
%{__mkdir} -p %{buildroot}%{_sharedstatedir}/%{name}

%pre
# create logstash group
if ! getent group logstash >/dev/null; then
    groupadd -r logstash
fi

# create logstash user
if ! getent passwd logstash >/dev/null; then
    useradd -r -g logstash -d %{_sharedstatedir}/%{name} -s /sbin/nologin -c "Logstash service user" logstash
fi

%post
/sbin/chkconfig --add logstash

%preun
if [ $1 -eq 0 ]; then
    /sbin/service logstash stop >/dev/null 2>&1
    /sbin/chkconfig --del logstash
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
# JAR file
%{__prefix}/%{name}/lib/%{name}.jar

# Config
%config(noreplace) %{_sysconfdir}/%{name}/logstash.conf

# Plugin dir
%dir %{__prefix}/%{name}/plugins/logstash/inputs
%dir %{__prefix}/%{name}/plugins/logstash/filters
%dir %{__prefix}/%{name}/plugins/logstash/outputs
%{__prefix}/%{name}/plugins/logstash/inputs/dummy.rb

# Logrotate
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

# Wrapper script
%{__prefix}/%{name}/bin/*

# Sysconfig and init
%{_initddir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/*

%defattr(-,%{name},%{name},-)
%dir %{_localstatedir}/log/%{name}/
%dir %{_localstatedir}/run/%{name}/

# Home directory
%dir %{_sharedstatedir}/%{name}/
