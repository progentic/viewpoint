import type { ReactNode } from "react"

import { App } from "./App"
import type { CompanionClient } from "./generated/client"
import type { OfficeReadyInfo, OfficeRuntime } from "./officeRuntime"
import type { TaskPaneStatus } from "./status"

export type ReactMount = (node: ReactNode) => void

export interface InitializationDependencies {
  office: OfficeRuntime
  client: CompanionClient
  mount: ReactMount
}

export async function initializeTaskPane(
  dependencies: InitializationDependencies,
): Promise<void> {
  const officeInfo = await dependencies.office.onReady()
  const unsupported = assessOfficeSupport(dependencies.office, officeInfo)
  if (unsupported !== null) {
    dependencies.mount(<App status={unsupported} />)
    return
  }
  await connectCompanion(dependencies, officeInfo)
}

function assessOfficeSupport(
  office: OfficeRuntime,
  info: OfficeReadyInfo,
): TaskPaneStatus | null {
  if (!office.isWord(info.host) || !office.isDesktop(info.platform)) {
    return unsupportedStatus("This spike supports Word Desktop on Windows and macOS only.")
  }
  if (!office.supportsWordApi13()) {
    return unsupportedStatus("This Word build does not support the required WordApi 1.3 set.")
  }
  return null
}

async function connectCompanion(
  dependencies: InitializationDependencies,
  info: OfficeReadyInfo,
): Promise<void> {
  try {
    await dependencies.client.bootstrapLocalSession(createBootstrapRequest(info))
    const health = await dependencies.client.getHealth()
    dependencies.mount(<App status={connectedStatus(health.version)} />)
  } catch {
    dependencies.mount(<App status={unavailableStatus()} />)
  }
}

function createBootstrapRequest(info: OfficeReadyInfo) {
  return {
    officeHost: "Word" as const,
    officePlatform: info.platform === "PC" ? ("PC" as const) : ("Mac" as const),
    wordApi13Supported: true as const,
  }
}

function connectedStatus(version: string): TaskPaneStatus {
  return {
    state: "connected",
    title: "Local companion connected",
    detail: `Authenticated health check succeeded. Companion ${version}.`,
  }
}

function unsupportedStatus(detail: string): TaskPaneStatus {
  return { state: "unsupported", title: "Unsupported Office host", detail }
}

function unavailableStatus(): TaskPaneStatus {
  return {
    state: "unavailable",
    title: "Local companion unavailable",
    detail: "The protected local health check could not be completed.",
  }
}
