{
  pkgs,
  lib,
  buildNpmPackage,
  ...
}:
buildNpmPackage {
  pname = "challenge-web";
  version = (lib.importJSON ./package.json).version;

  src = ./.;

  npmDepsHash = "sha256-b7knU/AG5Y3ODvduU+RjrjY14KUmuVRU/EK+G5i1jUk=";

  installPhase = ''
    runHook preInstall

    npm i -D

    cp -r build $out

    runHook postInstall
  '';
}
