import { StrictMode, type ReactNode } from "react"
import { createRoot, type Root } from "react-dom/client"

import { CompanionClient } from "./generated/client"
import { initializeTaskPane } from "./initialize"
import { OfficeJsRuntime } from "./officeRuntime"

function startTaskPane(): void {
  const rootElement = requireRootElement()
  if (globalThis.Office === undefined) {
    showOfficeUnavailable(rootElement)
    return
  }
  void initializeTaskPane({
    office: new OfficeJsRuntime(globalThis.Office),
    client: new CompanionClient(),
    mount: createDeferredReactMount(rootElement),
  })
}

function createDeferredReactMount(element: HTMLElement): (node: ReactNode) => void {
  let root: Root | null = null
  return (node) => {
    root ??= createRoot(element)
    root.render(<StrictMode>{node}</StrictMode>)
  }
}

function requireRootElement(): HTMLElement {
  const element = document.getElementById("root")
  if (element === null) {
    throw new Error("Task pane root is missing")
  }
  return element
}

function showOfficeUnavailable(element: HTMLElement): void {
  element.textContent = "Office.js is unavailable. Restart Word and the local companion."
  element.dataset.status = "unavailable"
}

startTaskPane()
