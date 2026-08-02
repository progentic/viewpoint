import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

describe("Office.js boot order", () => {
  it("loads production Office.js before the application module", () => {
    const indexPath = resolve(process.cwd(), "taskpane/index.html")
    const document = readFileSync(indexPath, "utf8")
    const officeScript = document.indexOf("https://appsforoffice.microsoft.com/lib/1/hosted/office.js")
    const applicationScript = document.indexOf('/src/startup.tsx')

    expect(officeScript).toBeGreaterThan(-1)
    expect(applicationScript).toBeGreaterThan(officeScript)
  })
})
