{
  description = "Minimal UV-to-NixOS devShell for testing solutions using nix-ld.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Define shortcuts using writeShellScriptBin
        # Use "$@" at the end so the script accepts extra flags/arguments
        uv-run = pkgs.writeShellScriptBin "uvr" "exec uv run \"$@\"";
        uv-sync = pkgs.writeShellScriptBin "uvs" "exec uv sync \"$@\"";
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            uv
            ruff

            # Inject shortcuts directly into the packages array
            uv-run
            uv-sync
          ];

          # Expose libraries to the nix-ld environment
          # NOTE: This devShell requires `programs.nix-ld.enable = true;` to be set in your
          # NixOS configuration (/etc/nixos/configuration.nix) to successfully run downloaded
          # pre-compiled binaries (e.g. PyPI dynamic wheels).
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
            pkgs.glib
          ];
        };
      });
}
