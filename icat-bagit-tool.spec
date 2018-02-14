Name:		icat-bagit-tool
Version:	1.0
Release:	1
Summary:	Export data from ICAT into BagIt packages
License:	Apache-2.0
Group:		Productivity/Scientific/Other
Source:		%{name}-%{version}.tar.gz
BuildRequires:  python3-devel
Requires:	python3-icat
Requires:	python3-bagit
Requires:	python3-lxml
BuildRoot:	%{_tmppath}/%{name}-%{version}-build
BuildArch:	noarch

%description
This tool implements the export scientific data from an ICAT into a
BagIt package as defined by the RDA Research Data Repository
Interoperability WG.


%prep
%setup -q


%build
python3 setup.py build


%install
python3 setup.py install --optimize=1 --prefix=%{_prefix} --root=%{buildroot}
mv %{buildroot}%{_bindir}/icat-bagit-export.py %{buildroot}%{_bindir}/icat-bagit-export


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc README.rst
%exclude %{python3_sitelib}/*
%{_bindir}/icat-bagit-export


%changelog
