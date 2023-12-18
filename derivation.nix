{ lib, python311Packages }:
with python311Packages;
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
in
buildPythonApplication {
    pname = "bob";
    version = "2.8.3";
    pyproject = true;

    nativeBuildInputs = [ hatchling ];

    propagatedBuildInputs = [
        discordpy
        levenshtein
        flask
        flask-cors
        nest-asyncio
        requests
        jishaku
        pynacl
        topggpy
    ];

    src = ./.;
}
