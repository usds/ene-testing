# Tests for Medicaid Systems
`generator.py` is a script that generates test case instances based on preconfigured test inputs (e.g. `testcase00001.yml`) as well as state configuration (e.g. `config_nj.yml`) and CMS-provided configuration (e.g. `fpl_tables.yml`).

# Usage
To run some sample tests, simply try `make test`.

Or to call the generator directly (not recommended): `python3 generator.py "config_aa.yml"` to run using state configuration AA.

# More Information
For more info see TODO
