# liscopridge

[![PyPI Python Version badge](https://img.shields.io/pypi/pyversions/liscopridge)](https://pypi.org/project/liscopridge/)
[![PyPI Version badge](https://img.shields.io/pypi/v/liscopridge)](https://pypi.org/project/liscopridge/)
![License badge](https://img.shields.io/github/license/liskin/liscopridge)

## Overview

liscopridge is a …

<!-- FIXME: example image -->

## Installation

Using [pipx][]:

```
pipx ensurepath
pipx install liscopridge
```

To keep a local git clone around:

```
git clone https://github.com/liskin/liscopridge
make -C liscopridge pipx
```

Alternatively, if you don't need the isolated virtualenv that [pipx][]
provides, feel free to just:

```
pip install liscopridge
```

[pipx]: https://github.com/pypa/pipx

## Usage

<!-- include tests/readme/help.md -->
    $ liscopridge --help
    Usage: liscopridge [OPTIONS]
    
    Options:
      --config FILE    Read configuration from FILE.  [default:
                       /home/user/.config/liscopridge/config.yaml]
      --config-sample  Show sample configuration file
      --help           Show this message and exit.
<!-- end include tests/readme/help.md -->

<!-- FIXME: example -->

### Configuration file

Secrets (and other options) can be set permanently in a config file,
which is located at `~/.config/liscopridge/config.yaml` by default
(on Linux; on other platforms see output of `--help`).

Sample config file can be generated using the `--config-sample` flag:

<!-- include tests/readme/config-sample.md -->
    $ liscopridge --config-sample
<!-- end include tests/readme/config-sample.md -->
