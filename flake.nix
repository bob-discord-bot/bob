{
  description = "bob - a plug-n-play Discord chat bot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system: 
    let
      pkgs = nixpkgs.legacyPackages.${system};
      deps = pkgs.callPackage ./nix/dependencies.nix {};
    in {
      packages = rec {
        bob = with pkgs.python311Packages; buildPythonApplication {
          pname = "bob";
          version = "3.0.0-alpha";
          pyproject = true;
          nativeBuildInputs = [ hatchling ];

          propagatedBuildInputs = [
            discordpy
            levenshtein
            flask
            flask-cors
            nest-asyncio
            deps.jishaku
            pynacl
            deps.topggpy
            deps.tortoiseORM
            deps.aerich
          ];

          src = ./.;
        };
        default = bob;
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs.python311Packages; [
          discordpy
          levenshtein
          flask
          flask-cors
          nest-asyncio
          deps.jishaku
          pynacl
          deps.topggpy
          deps.tortoiseORM
          asyncpg
          deps.aerich
        ];
      };
    }
  );
}
