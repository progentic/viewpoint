import { existsSync } from "node:fs"
import { spawnSync } from "node:child_process"
import { resolve } from "node:path"

const projectRoot = resolve(import.meta.dirname, "..")
const python = resolve(
  projectRoot,
  process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python",
)

if (!existsSync(python)) {
  console.error("Missing locked Python environment; create .venv and install requirements.lock")
  process.exit(1)
}

const environment = {
  ...process.env,
  PHASE1_NODE_EXECUTABLE: process.execPath,
}
const completed = spawnSync(python, process.argv.slice(2), {
  cwd: projectRoot,
  env: environment,
  stdio: "inherit",
})

if (completed.error) {
  throw completed.error
}
process.exit(completed.status ?? 1)
