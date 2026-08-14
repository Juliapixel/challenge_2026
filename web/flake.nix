{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-26.05";
  };

  outputs = inputs: {
    packages = builtins.mapAttrs (system: pkgs: {
      default = pkgs.callPackage ./. { };
    }) inputs.nixpkgs.legacyPackages;

    devShells = builtins.mapAttrs (system: pkgs: {
      default = pkgs.mkShell {
        packages = [
          pkgs.nodejs_26
        ];
      };
    }) inputs.nixpkgs.legacyPackages;

    apps = builtins.mapAttrs (system: pkgs: {
      dev = {
        type = "app";
        program = toString (pkgs.writeShellScript "host-challenge-web" ''
        set -euxo pipefail
        ${pkgs.lib.getExe pkgs.miniserve} \
        --index index.html \
        --header 'Content-Security-Policy:script-src self;' \
        --header 'Content-Security-Policy-Report-Only:report-uri /; img-src 'self' *; frame-src *; connect-src 'self' *; font-src 'self' *; style-src 'self' unsafe-inline *; worker-src *' \
        "$(nix build .#default --print-out-paths)" \
        '');
      };
    }) inputs.nixpkgs.legacyPackages;
  };
}
