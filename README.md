# yabp

Yet Another Bus Pirate Libray

A [Bus Pirate](http://dangerousprototypes.com/docs/Bus_Pirate) is a handy little debug tool.  Its
firmware, command documentation and artwork are released into the public domain.  This is another library but fits my needs and doesn't carry the GPL notice that is tucked away in the *pyBusPirateLite*
that is under the scripts folder or any derivative.  They have gone untouched and updated for many years.

## Developer Install

1. `git clone https://github.com/jdpatt/yabp.git`
2. `cd yabp`
3. Create a virtual environment with `virtualenv .venv`
4. [Activate that environment](https://virtualenv.pypa.io/en/latest/)
5. `pip install -r requirements-dev.txt`
6. `pre-commit install`
7. `pip install -e .`
8. `tox`
