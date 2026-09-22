{
  pkgs ? import <nixpkgs> { },
}: pkgs.buildGoModule {
  pname = "coletor";
  version = "0-unstable";

  src = ./.;

  nativeBuildInputs = [
    pkgs.pkg-config
  ];

  buildInputs = [
    pkgs.x264
  ];

  subPackages = [
    "cmd/client"
  ];

  vendorHash = "sha256-031qRrekwivKMYLdkWzzG8L2MKmqz/vStCHNTG3XGbc=";
}
