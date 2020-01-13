Summary: Content for the Anaconda built-in help system
Name: anaconda-user-help
Patch1:	debrand_anaconda_user_help.patch
Patch2:	eurolinux_rebrand.patch
URL: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/Installation_Guide
Version: 7.5.3
Release: 2%{?dist}
Epoch: 1
BuildArch: noarch

# This is a Red Hat maintained package which is specific to
# our distribution.
#
# The source is thus available only from within this SRPM.
Source0: %{name}-%{version}.tar.gz
Source2:	anaconda-user-help.ini

License: CC-BY-SA
Group: System Environment/Base
BuildRequires: python2-devel
BuildRequires: python-lxml

%description
This package provides content for the Anaconda built-in help system.

%prep
%setup -q
%patch1 -p1
%patch2 -p1

%build
python prepare_anaconda_help_content.py

%install
mkdir -p %{buildroot}%{_datadir}/anaconda/help
cp -r anaconda_help_content/* %{buildroot}%{_datadir}/anaconda/help

%files
%{_datadir}/anaconda/help/*

%changelog
* Mon Dec 23 2019 Aleksander Baranowski <aleksander.baranowski@euro-linux.com> - 7.5.3-2
- Rebuild for new build system.

* Wed May 23 2018 Aleksander Baranowski <aleksander.baranowski@euro-linux.com>
- Add EuroLinux Patch

* Fri Apr 13 2018 Scientific Linux Auto Patch Process <SCIENTIFIC-LINUX-DEVEL@LISTSERV.FNAL.GOV>
- Added Source: anaconda-user-help.ini
-->  Config file for automated patch script
- Added Patch: debrand_anaconda_user_help.patch
-->  Debrand help files

* Thu Oct 06 2017 Martin Kolman <mkolman@redhat.com> - 7.5.3-1
- Add RHV branded help content variant (mkolman)
  Resolves: rhbz#1378010

* Thu Jun 30 2016 Martin Kolman <mkolman@redhat.com> - 7.3.2-1
- Document the fadump option for the Kdump Anaconda addon (cspicer)
  Resolves: rhbz#1260880

* Thu May 12 2016 Martin Kolman <mkolman@redhat.com> - 7.3.1-1
- Bump epoch to fix upgrades from the Anaconda help content subpackage (mkolman)
  Resolves: rhbz#1275285
- Add help content for the Subscription Manager addon spoke (cspicer)
  Resolves: rhbz#1260071

* Fri Aug 28 2015 Martin Kolman <mkolman@redhat.com> - 7.2.2-1
- Add InitialSetupHub-common to help generator script (pbokoc)
  Resolves: rhbz#1247779

* Mon Aug 24 2015 Martin Kolman <mkolman@redhat.com> - 7.2.1-1
- Update help content to account for 7.2 additions and changes
  Resolves: rhbz#1256407

* Tue Jun 16 2015 Martin Kolman <mkolman@redhat.com> - 7.1.8-1
- Initial release (mkolman)
  Resolves: rhbz#1224974
