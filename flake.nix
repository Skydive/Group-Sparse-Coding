{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.nixpkgs.follows = "nixpkgs";
    mach-nix.url = "github:DavHau/mach-nix?ref=3.5.0";
  };

  outputs = { self, nixpkgs, flake-utils, mach-nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      python = "python38";
      pkgs = import nixpkgs { inherit system; };
      mach-nix-wrapper = import mach-nix { inherit pkgs python; };
      requirements = builtins.readFile ./requirements.txt;
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
            pythonBuild
          ];

          propagatedBuildInputs = [
            pkgs.stdenv.cc.cc.lib
          ];
        };
    });
}
