%global with_doc 1
%global prj glance

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:             openstack-%{prj}
Version:          0.1.2
Release:          1
Summary:          OpenStack Image Registry and Delivery Service

Group:            Development/Languages
License:          ASL 2.0
URL:              http://%{prj}.openstack.org
Source0:          http://launchpad.net/glance/bexar/%{version}/+download/%{prj}-%{version}.tar.gz
Source1:          %{name}.conf
Source2:          %{name}.init

BuildRoot:        %{_tmppath}/%{prj}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:        noarch
BuildRequires:    python-devel
BuildRequires:    python-setuptools

Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils
Requires:         python-%{prj} = %{version}-%{release}

%description
The Glance project provides an image registration and discovery service (Parallax)
and an image delivery service (Teller). These services are used in conjunction
by Nova to deliver images from object stores, such as OpenStack's Swift service,
to Nova's compute nodes.

This package contains the API server and reference implementation server.

%package -n       python-%{prj}
Summary:          Glance Python libraries
Group:            Applications/System

Requires:         python-anyjson
Requires:         python-daemon = 1.5.5
Requires:         python-eventlet >= 0.9.12
Requires:         python-gflags >= 1.3
Requires:         python-lockfile = 0.8
Requires:         python-mox >= 0.5.0
Requires:         python-routes
Requires:         python-sqlalchemy >= 0.6.3
Requires:         python-webob

%description -n   python-%{prj}
The Glance project provides an image registration and discovery service (Parallax)
and an image delivery service (Teller). These services are used in conjunction
by Nova to deliver images from object stores, such as OpenStack's Swift service,
to Nova's compute nodes.

This package contains the project's Python library.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Glance
Group:            Documentation

BuildRequires:    python-sphinx
BuildRequires:    python-nose
# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-daemon
BuildRequires:    python-eventlet
BuildRequires:    python-gflags
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob

%description      doc
The Glance project provides an image registration and discovery service (Parallax)
and an image delivery service (Teller). These services are used in conjunction
by Nova to deliver images from object stores, such as OpenStack's Swift service,
to Nova's compute nodes.

This package contains documentation files for OpenStack Glance.
%endif

%prep
%setup -q -n %{prj}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

%if 0%{?with_doc}
export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
sphinx-build -b html source build/html
popd

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{prj}/images

# Config file
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/nova/%{prj}.conf

# Initscript
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

%clean
rm -rf %{buildroot}

%pre
getent group %{prj} >/dev/null || groupadd -r %{prj}
getent passwd %{prj} >/dev/null || \
useradd -r -g %{prj} -d %{_sharedstatedir}/%{prj} -s /sbin/nologin \
-c "OpenStack Glance Daemon" %{prj}
exit 0

%post
/sbin/chkconfig --add openstack-%{prj}

%preun
if [ $1 = 0 ] ; then
    /sbin/service openstack-%{prj} stop
    /sbin/chkconfig --del openstack-%{prj}
fi

%files
%defattr(-,root,root,-)
%doc README
%{_bindir}/%{prj}-api
%{_bindir}/%{prj}-registry
%{_initrddir}/%{name}
%defattr(-,%{prj},nobody,-)
%config(noreplace) %{_sysconfdir}/nova/%{prj}.conf
%dir %{_sharedstatedir}/%{prj}

%files -n python-%{prj}
%{python_sitelib}/%{prj}
%{python_sitelib}/%{prj}-%{version}-*.egg-info

%if 0%{?with_doc}
%files doc
%defattr(-,root,root,-)
%doc doc/build/html
%endif

%changelog
* Thu Jan 20 2011 Andrey Brindeyev <abrindeyev@griddynamics.com> 0.1.2-1
- Initial build
