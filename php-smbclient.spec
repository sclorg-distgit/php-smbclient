# centos/sclo spec file for php-smbclient, from:
#
# remirepo spec file for php-smbclient
#
# Copyright (c) 2015-2019 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%global sub_prefix %{scl_prefix}
%if "%{scl}" == "rh-php70"
%global sub_prefix sclo-php70-
%endif
%if "%{scl}" == "rh-php71"
%global sub_prefix sclo-php71-
%endif
%if "%{scl}" == "rh-php72"
%global sub_prefix sclo-php72-
%endif
%if "%{scl}" == "rh-php73"
%global sub_prefix sclo-php73-
%endif
%scl_package       php-smbclient
%else
%global pkg_name   %{name}
%endif

%global pecl_name  smbclient
%global ini_name   40-%{pecl_name}.ini

Name:           %{?sub_prefix}php-smbclient
Version:        1.0.0
Release:        2%{?dist}

Summary:        PHP wrapper for libsmbclient

Group:          Development/Languages
License:        BSD
URL:            https://github.com/eduardok/libsmbclient-php
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRequires:  %{?scl_prefix}php-devel
BuildRequires:  %{?scl_prefix}php-pear
BuildRequires:  libsmbclient-devel > 3.6

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}

%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:       %{?scl_prefix}php-%{pecl_name}               = %{version}-%{release}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa}       = %{version}-%{release}
%endif
# PECL
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})         = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
%{pecl_name} is a PHP extension that uses Samba's libsmbclient
library to provide Samba related functions and 'smb' streams
to PHP programs.


%prep
%setup -q -c
mv %{pecl_name}-%{version}%{?prever} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    %{?_licensedir:-e '/LICENSE/s/role="doc"/role="src"/' } \
    -i package.xml

cd NTS
# Check extension version
ver=$(sed -n '/define PHP_SMBCLIENT_VERSION/{s/.* "//;s/".*$//;p}' php_smbclient.h)
if test "$ver" != "%{version}%{?prever}%{?gh_date:-dev}"; then
   : Error: Upstream VERSION version is ${ver}, expecting %{version}%{?prever}%{?gh_date:-dev}.
   exit 1
fi
cd ..

cat  << 'EOF' | tee %{ini_name}
; Enable %{summary} extension module
extension=%{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install configuration
install -Dpm 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%{?_licensedir:%license NTS/LICENSE}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%changelog
* Mon Oct 28 2019 Remi Collet <remi@remirepo.net> - 1.0.0-2
- build for sclo-php73

* Wed Dec 26 2018 Remi Collet <remi@remirepo.net> - 1.0.0-1
- update to 1.0.0

* Thu Nov 15 2018 Remi Collet <remi@remirepo.net> - 0.9.0-3
- build for sclo-php72

* Thu Aug 10 2017 Remi Collet <remi@remirepo.net> - 0.9.0-2
- change for sclo-php71

* Tue Mar  7 2017 Remi Collet <remi@fedoraproject.org> - 0.9.0-1
- cleanup for SCLo build

* Fri Feb 10 2017 Remi Collet <remi@fedoraproject.org> - 0.9.0-1
- update to 0.9.0 (stable)

* Thu Dec  1 2016 Remi Collet <remi@fedoraproject.org> - 0.9.0-0.2.20161104git1857016
- rebuild with PHP 7.1.0 GA

* Tue Nov  8 2016 Remi Collet <remi@fedoraproject.org> - 0.9.0-0.1.20161104git1857016
- update to 0.9.0-dev for stream performance

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 0.8.0-2
- rebuild for PHP 7.1 new API version

* Wed Mar  2 2016 Remi Collet <remi@fedoraproject.org> - 0.8.0-1
- update to 0.8.0 (stable, no change)

* Tue Dec  8 2015 Remi Collet <remi@fedoraproject.org> - 0.8.0-0.5.RC1
- now available on PECL

* Tue Oct 13 2015 Remi Collet <remi@fedoraproject.org> - 0.8.0-0.4.rc1
- rebuild for PHP 7.0.0RC5 new API version

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 0.8.0-0.3.rc1
- F23 rebuild with rh_layout

* Wed Sep 16 2015 Remi Collet <rcollet@redhat.com> - 0.8.0-0.2.rc1
- update to 0.8.0-rc1
- rename from php-libsmbclient to php-smbclient
- https://github.com/eduardok/libsmbclient-php/pull/26 rename

* Thu Sep  3 2015 Remi Collet <rcollet@redhat.com> - 0.8.0-0.1.20150909gita65127d
- update to 0.8.0-dev
- https://github.com/eduardok/libsmbclient-php/pull/20 streams support
- https://github.com/eduardok/libsmbclient-php/pull/23 PHP 7

* Thu Sep  3 2015 Remi Collet <rcollet@redhat.com> - 0.7.0-1
- Update to 0.7.0
- drop patches merged upstream
- license is now BSD

* Wed Sep  2 2015 Remi Collet <rcollet@redhat.com> - 0.6.1-1
- Initial packaging of 0.6.1
- open https://github.com/eduardok/libsmbclient-php/pull/17
  test suite configuration
- open https://github.com/eduardok/libsmbclient-php/pull/18
  add reflection and improve phpinfo
- open https://github.com/eduardok/libsmbclient-php/issues/19
  missing license file
