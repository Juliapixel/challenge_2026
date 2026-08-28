{
  pkgs ? import <nixpkgs> { },
}:
(pkgs.mkShell {
  name = "coletor";

  packages = [
    pkgs.x264
    pkgs.go
    pkgs.pkg-config
  ];

  extraOutputsToInstall = [
    "dev"
    "out"
    "lib"
  ];
})
