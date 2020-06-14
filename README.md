# yabp

Yet Another Bus Pirate Libray

A [Bus Pirate](http://dangerousprototypes.com/docs/Bus_Pirate) is a handy little debug tool.  Its
firmware, command documentation and artwork are released into the public domain.  This is another library built from the command documentation but fits my needs and doesn't carry the GPL notice that is tucked away in the *pyBusPirateLite* that is under the scripts folder or any similar derivatives.  They have gone untouched for many years.

## Developer Install

1. `git clone https://github.com/jdpatt/yabp.git`
2. `cd yabp`
3. Create a virtual environment with `python -m venv .venv`
4. Activate that environment
5. `pip install -r requirements-dev.txt`
6. `pre-commit install`
7. `pip install -e .`
8. `tox`
