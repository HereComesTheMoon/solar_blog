let
  # We pin to a specific nixpkgs commit for reproducibility.
  # Last updated: 2024-11-01. Check for new commits at https://lazamar.co.uk/nix-versions/?channel=nixpkgs-24.05-darwin&package=python3
  pkgs = import (fetchTarball
    "https://github.com/NixOS/nixpkgs/archive/42c5e250a8a9162c3e962c78a4c393c5ac369093.tar.gz")
    { };

in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs:
      [
        # select Python packages here
        python-pkgs.beautifulsoup4
        python-pkgs.pillow
        python-pkgs.numpy
      ]))
  ];
}

