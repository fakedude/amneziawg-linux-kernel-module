%global debug_package %{nil}

Name:           amneziawg-dkms
Version:        1.0.20240806
Release:        1%{?dist}
Epoch:          1
URL:            https://www.wireguard.com/
Summary:        Fast, modern, secure VPN tunnel
License:        GPLv2
Group:          System Environment/Kernel
BuildArch:      noarch

Source0:        https://github.com/amnezia-vpn/amneziawg-linux-kernel-module/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/fakedude/amneziawg-linux-kernel-module/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  kernel-devel
BuildRequires:  sed
BuildRequires:  make
BuildRequires:  bc

Provides:       kmod(amneziawg.ko) = %{epoch}:%{version}-%{release}
Requires:       dkms
Requires:       kernel-devel
Requires:       make
Requires:       bc
Requires:       yum-utils
Requires:       rpm-build
Requires:       python3-devel

%description
WireGuard is a novel VPN that runs inside the Linux Kernel and uses
state-of-the-art cryptography (the "Noise" protocol). It aims to be
faster, simpler, leaner, and more useful than IPSec, while avoiding
the massive headache. It intends to be considerably more performant
than OpenVPN. WireGuard is designed as a general purpose VPN for
running on embedded interfaces and super computers alike, fit for
many different circumstances. It runs over UDP.

%prep
%autosetup -p1 -n amneziawg-linux-kernel-module-%{version}

# Fix the Makefile for CentOS7 since it ships coreutils from 2013.
sed -i 's/install .* -D -t\(.\+\) /mkdir -p \1 \&\& \0/' %{_builddir}/amneziawg-linux-kernel-module-%{version}/src/Makefile

# Set version in dkms.conf and Makefile
sed -i "s/^PACKAGE_VERSION=.*/PACKAGE_VERSION=\"%{version}\"/" %{_builddir}/amneziawg-linux-kernel-module-%{version}/src/dkms.conf
sed -i "s/^WIREGUARD_VERSION = .*/WIREGUARD_VERSION = %{version}/" %{_builddir}/amneziawg-linux-kernel-module-%{version}/src/Makefile

%build

%install
mkdir -p %{buildroot}%{_usrsrc}/amneziawg-%{version}/
make DESTDIR=%{buildroot} DKMSDIR=%{_usrsrc}/amneziawg-%{version}/ \
    -C %{_builddir}/amneziawg-linux-kernel-module-%{version}/src dkms-install

%post
dkms add -m amneziawg -v %{version} --rpm_safe_upgrade || :
dkms build -m amneziawg -v %{version} || :
dkms install -m amneziawg -v %{version} --force || :
echo "amneziawg-dkms-%{version}-%{release}" > /var/lib/dkms/amneziawg/%{version}/version

%preun
# Check if we are running an upgrade
if [ $1 -ne 0 ]; then
  WG_VERSION=$(dkms status amneziawg|grep installed|sort -r -V|awk '{print $2}'|cut -f1 -d,)
  if [ "$WG_VERSION" != "%{version}" ] ; then

    true

  else

    exit 0

  fi
fi

# If we are not running an upgrade then remove everything!
WG_VERSION_FILE=$(cat /var/lib/dkms/amneziawg/%{version}/version)
WG_RPM_VERSION=amneziawg-dkms-%{version}-%{release}
if [ "$WG_RPM_VERSION" = "$WG_VERSION_FILE" ]; then

    dkms remove -m amneziawg -v %{version} -q --all --rpm_safe_upgrade || :

fi

exit 0

%files
%{_usrsrc}/amneziawg-%{version}

%changelog
%autochangelog
