import type { ReactElement, ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

import type { CompanionClient } from "../src/generated/client"
import { initializeTaskPane } from "../src/initialize"
import type { OfficeReadyInfo, OfficeRuntime } from "../src/officeRuntime"
import type { TaskPaneStatus } from "../src/status"

describe("task-pane initialization", () => {
  it("does not mount React before Office.onReady resolves", async () => {
    let resolveOffice: ((info: OfficeReadyInfo) => void) | undefined
    const onReady = new Promise<OfficeReadyInfo>((resolve) => {
      resolveOffice = resolve
    })
    const mount = vi.fn<(node: ReactNode) => void>()
    const initialization = initializeTaskPane({
      office: officeRuntime(onReady, true),
      client: connectedClient(),
      mount,
    })

    expect(mount).not.toHaveBeenCalled()
    resolveOffice?.({ host: "Word", platform: "Mac" })
    await initialization
    expect(readStatus(mount).state).toBe("connected")
    expect(readStatus(mount).detail).toContain("WordApi 1.3 confirmed")
  })

  it("shows unsupported when the host is not Word Desktop", async () => {
    const mount = vi.fn<(node: ReactNode) => void>()
    const client = connectedClient()

    await initializeTaskPane({
      office: officeRuntime(Promise.resolve({ host: "Excel", platform: "Mac" }), true),
      client,
      mount,
    })

    expect(readStatus(mount).state).toBe("unsupported")
    expect(client.bootstrapLocalSession).not.toHaveBeenCalled()
  })

  it("shows unsupported when WordApi 1.3 is missing", async () => {
    const mount = vi.fn<(node: ReactNode) => void>()

    await initializeTaskPane({
      office: officeRuntime(Promise.resolve({ host: "Word", platform: "PC" }), false),
      client: connectedClient(),
      mount,
    })

    expect(readStatus(mount).state).toBe("unsupported")
    expect(readStatus(mount).detail).toContain("WordApi 1.3")
  })
})

function officeRuntime(ready: Promise<OfficeReadyInfo>, supportsWordApi13: boolean): OfficeRuntime {
  return {
    onReady: () => ready,
    isWord: (host) => host === "Word",
    isDesktop: (platform) => platform === "PC" || platform === "Mac",
    supportsWordApi13: () => supportsWordApi13,
  }
}

function connectedClient(): CompanionClient {
  return {
    bootstrapLocalSession: vi.fn().mockResolvedValue({ csrfToken: "session", expiresAt: "soon" }),
    getHealth: vi.fn().mockResolvedValue({
      schemaVersion: 1,
      status: "ok",
      version: "0.1.0",
      components: { database: "ready", contentStore: "ready", worker: "ready" },
    }),
  } as unknown as CompanionClient
}

function readStatus(mount: ReturnType<typeof vi.fn>): TaskPaneStatus {
  const element = mount.mock.calls[0][0] as ReactElement<{ status: TaskPaneStatus }>
  return element.props.status
}
