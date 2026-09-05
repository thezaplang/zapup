# zapup
The Zap toolchain installer

## Source toolchains after the LSP split

`zapup install --src [lsp_commit_sha]` selects a revision of
`thezaplang/zap-lsp`, not a compiler commit. Its `subprojects/zap` gitlink
selects the matching compiler. Recursive submodules are fetched before building.
The compiler, server, runtime object, `core`, and `std` are installed together
under `versions/lsp-<commit>/build-toolchain/stage/bin`.

Source installation requires Git, Bash, Meson, Ninja, a C/C++17 compiler,
LLVM 21 or newer, and OpenSSL development files. Node.js/npm is needed only
when choosing to build the VS Code extension. Binary release downloads still
come from `thezaplang/zap`; their combined archives are assembled in `zap-lsp`.

## Validation

Using a compiler from the pinned toolchain:

```bash
mkdir -p build
zapc src/main.zp -o build/zapup
zapc tests/release_metadata_test.zp -o build/release_metadata_test
./build/release_metadata_test
python3 tests/source_install_test.py /absolute/path/to/zapc
```

The source installation tests substitute Git/build/Thor fixtures and use a
temporary home directory. They cover latest and pinned LSP revisions and a
failed recursive submodule fetch without contacting GitHub or changing shell
configuration. Release metadata tests cover the current `std/json` API,
including malformed responses and incorrectly typed assets.

The existing source installer retains failed checkouts for inspection. After a
failure, remove its `.zapup-source-tmp` directory or incomplete `lsp-<commit>`
checkout under the versions directory before retrying; the current installer
does not resume partial source installations. Automatic cleanup/resume remains
separate from the repository migration.
