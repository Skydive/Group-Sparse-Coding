{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.nixpkgs.follows = "nixpkgs";
    pypi-deps-db = {
      flake = false;
      url = "github:DavHau/pypi-deps-db";
    };
    mach-nix = {
      url = "github:DavHau/mach-nix/3.5.0";
      inputs.pypi-deps-db.follows = "pypi-deps-db";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, mach-nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      python = "python38Full";
      pkgs = import nixpkgs { inherit system; };
      mach-nix-wrapper = import mach-nix { inherit pkgs python; };
      requirements = builtins.readFile ./requirements-flake.txt;
      providers = {
        _default = "wheel,nixpkgs,sdist";
        "torch" = "wheel"; 
        "pillow" = "wheel"; 
        "pandas" = "wheel"; 
        "numpy" = "wheel"; 
        "opencv-python" = "wheel"; 
      };
      pythonBuild = mach-nix-wrapper.mkPython { inherit requirements providers; };
    in {
      devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            #(pkgs.${python}.withPackages
            #  (ps: with ps; [ pip tkinter ]))
            tk
            pythonBuild
          ];

          propagatedBuildInputs = [
            pkgs.stdenv.cc.cc.lib
          ];
        };
    });
}
