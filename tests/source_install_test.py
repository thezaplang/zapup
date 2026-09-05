#!/usr/bin/env python3
"""Run the source installer with local Git/build/Thor fixtures and a temporary HOME."""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMIT = "a" * 40
FAKE_GIT = '''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ["GIT_TRACE_FILE"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if args[0] in ("clone", "init"):
    directory = pathlib.Path(args[-1])
    directory.mkdir(parents=True)
    (directory / "build-toolchain.sh").write_text("#!/usr/bin/env bash\\nset -eu\\ncd \\\"$(dirname \\\"$0\\\")\\\"\\nmkdir -p build-toolchain/stage/bin\\nprintf built > build-toolchain/stage/bin/zapc\\nprintf built > build-toolchain/stage/bin/zap-lsp\\n")
elif "rev-parse" in args:
    print("a" * 40)
elif "submodule" in args and os.environ.get("FAIL_SUBMODULE"):
    sys.exit(1)
'''


def main():
    compiler = str(pathlib.Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory(prefix="zapup-source-test-") as temporary:
        root = pathlib.Path(temporary)
        fixture = root / "fixture"
        fixture.mkdir()
        for name in ["source.zp", "shell.zp"]:
            shutil.copy2(ROOT / "src" / name, fixture / name)
        (fixture / "thor.zp").write_text('import "std/fs"; pub fun install(binDir: String) Int { if !fs.exists(binDir + "/zapc") || !fs.exists(binDir + "/zap-lsp") { return 1; } return 0; }\n')
        (fixture / "main.zp").write_text(
            'import "source"; import "std/process";\n'
            'fun main() Int { return source.install(process.argv(1)); }\n'
        )
        binary = root / "installer"
        subprocess.run([compiler, str(fixture / "main.zp"), "-o", str(binary)], check=True)
        tools = root / "tools"
        tools.mkdir()
        git = tools / "git"
        git.write_text(FAKE_GIT)
        git.chmod(0o755)
        for case, requested, failure in [("latest", "", False), ("pinned", COMMIT, False), ("failure", COMMIT, True)]:
            home = root / (case + " user's home")
            home.mkdir()
            trace = root / (case + ".jsonl")
            env = {**os.environ, "HOME": str(home), "PATH": str(tools) + os.pathsep + os.environ["PATH"],
                   "GIT_TRACE_FILE": str(trace)}
            if failure:
                env["FAIL_SUBMODULE"] = "1"
            result = subprocess.run([str(binary), requested], input="n\n\n", text=True,
                                    capture_output=True, env=env, timeout=30)
            assert result.returncode == (4 if failure else 0), (case, result.stdout, result.stderr)
            commands = [json.loads(line) for line in trace.read_text().splitlines()]
            assert any("https://github.com/thezaplang/zap-lsp.git" in command for command in commands)
            assert any(command[-4:] == ["submodule", "update", "--init", "--recursive"] for command in commands)
            if requested:
                assert any(command[-5:] == ["fetch", "--depth", "1", "origin", requested] for command in commands)
            installed = home / ".local/share/zapup/versions" / ("lsp-" + COMMIT)
            if failure:
                assert not installed.exists()
            else:
                assert (installed / "build-toolchain/stage/bin/zapc").is_file()
                assert (installed / "build-toolchain/stage/bin/zap-lsp").is_file()
                assert not (home / ".bashrc").exists()
        print("source install: latest, pinned, and submodule failure passed")


if __name__ == "__main__":
    main()
