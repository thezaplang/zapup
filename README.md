# zapup

The Zap toolchain installer.

`zapup` installs and manages Zap toolchain versions.

## Install from source

Install the latest toolchain from source:

```bash
zapup install --src
```

Install a specific `zap-lsp` revision:

```bash
zapup install --src <commit>
```

Source builds use the compiler revision pinned by `zap-lsp`, ensuring that
`zapc`, `zap-lsp`, `runtime.o`, `core/`, and `std/` come from the same
toolchain version.

Installed source toolchains are stored under:

```text
versions/lsp-<commit>/
```

### Requirements

Source installation requires:

* Git
* Bash
* Meson
* Ninja
* C++17 compiler
* LLVM 21+
* OpenSSL development files

Node.js and npm are only required when building the VS Code extension.

## Binary releases

Binary installations are downloaded from Zap releases.

Release archives contain the complete toolchain, including:

```text
zapc
zap-lsp
runtime.o
core/
std/
```

## Development

Build `zapup` and run its tests with:

```bash
mkdir -p build

zapc src/main.zp -o build/zapup
zapc tests/release_metadata_test.zp -o build/release_metadata_test

./build/release_metadata_test
python3 tests/source_install_test.py /absolute/path/to/zapc
```

The tests cover source installations, pinned revisions, submodule failures,
and release metadata handling.

## Troubleshooting

A failed source installation may leave an incomplete checkout behind.

Before retrying, remove either:

```text
.zapup-source-tmp
```

or the incomplete:

```text
versions/lsp-<commit>
```
