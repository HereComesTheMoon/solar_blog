{ buildPythonPackage, python3Packages, setuptools }:

buildPythonPackage {
  pname = "hitherdither";
  version = "0.15.0";

  src = fetchGit { url = "https://github.com/hbldh/hitherdither.git"; };

  # specific to buildPythonPackage, see its reference
  pyproject = true;
  build-system = [ setuptools ];

  dependencies = [ python3Packages.numpy python3Packages.pillow ];
}
