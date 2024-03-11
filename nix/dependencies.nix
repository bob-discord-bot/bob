{ pkgs, lib, fetchFromGitHub }:
with pkgs.python311Packages;
let
    import_expression = buildPythonPackage rec {
        pname = "import_expression";
        version = "1.1.4";
        src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-BghqarO/pSixxHjmM9at8rOpkOMUQPZAGw8+oSsGWak=";
        };
        doCheck = false;
        propagatedBuildInputs = [
            astunparse
        ];
    };

    pypikaTortoise = buildPythonPackage rec {
        pname = "pypika-tortoise";
        version = "0.1.6";
        src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-2AKGj0eacI4yY3JMe1cZomrXk5mypwzqBl9KTK2+vzY=";
        };
        pyproject = true;

        nativeBuildInputs = [
            poetry-core
        ];
    };
in
rec {
    jishaku = buildPythonPackage rec {
        pname = "jishaku";
        version = "2.5.2";
        src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-VtOMMzA243SB3148noHWAztQl3OPDRcageJ1ISTw31w=";
        };
        doCheck = false;
        propagatedBuildInputs = [
            braceexpand
            click
            import_expression
            tabulate
        ];
    };

    topggpy = buildPythonPackage rec {
        pname = "topggpy";
        version = "1.4.0";
        src = fetchPypi {
            inherit pname version;
            sha256 = "sha256-daLzARoHPAWCOLdAmJFVzIVZglDtYFt4i13ijEMU7AQ=";
        };
        doCheck = false;
        propagatedBuildInputs = [
            aiohttp
        ];
    };

    tortoiseORM = buildPythonPackage rec {
        pname = "tortoise-orm";
        version = "0.20.0";
        src = fetchPypi {
            pname = "tortoise_orm";
            inherit version;
            sha256 = "sha256-KDr1hNaF3MWNbMHaNbkRW7HkHIkHXq4qGcSTs5ubQfc=";
        };
        doCheck = false;
        pyproject = true;
        
        nativeBuildInputs = [
            poetry-core
        ];

        propagatedBuildInputs = [
            pypikaTortoise
            (iso8601.overrideAttrs(old: rec {
                version = "1.1.0";
                src = fetchPypi {
                    pname = "iso8601";
                    inherit version;
                    hash = "sha256-MoEee4He7iBj6m0ulPiBmobR84EeSdI2I6QfqDK+8D8=";
                };
            }))
            (aiosqlite.overrideAttrs(old: rec {
                version = "0.16.0";
                src = fetchPypi {
                    pname = "aiosqlite";
                    inherit version;
                    sha256 = "1a0fjmlvadyzsml10g5p1qif7192k0swy5zwjp8v48y5zc3yy56h";
                };
                propagatedBuildInputs = [
                    typing-extensions
                    aiounittest
                ];
            }))
            pytz
        ];
    };

    aerich = buildPythonPackage rec {
        pname = "aerich";
        version = "2023-12-26";
        src = fetchFromGitHub {
            owner = "tortoise";
            repo = "aerich";
            rev = "ede53ade867f5e0a0a3f64c7363ab6decf5bd3c5";
            hash = "sha256-8zW9NH4OI7N9FnhfqNkEgEvzhFTnwxDHDMu1K26pGZE=";
        };
        doCheck = false;
        pyproject = true;
        
        nativeBuildInputs = [
            poetry-core
        ];

        propagatedBuildInputs = [
            tortoiseORM
            click
            pydantic
            dictdiffer
            tomlkit
        ];
    };
}
