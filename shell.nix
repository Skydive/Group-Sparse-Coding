# shell.nix
{ pkgs ? import <nixpkgs> {} }:
let
  my-python = pkgs.python39;
  python-with-my-packages = my-python.withPackages (p: with p; [
    pip
    tkinter
    virtualenv
    # numpy
    # pandas

    # ipykernel
    # jupyter
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pkgs.tk
    python-with-my-packages
  ];
  propagatedBuildInputs = [
    pkgs.stdenv.cc.cc.lib
  ];
  shellHook = ''
    PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pop install ipywidgets
    pip install notebook
    export LD_LIBRARY_PATH=$(nix eval --raw nixpkgs#stdenv.cc.cc.lib)/lib
    jupyter notebook
  '';
}