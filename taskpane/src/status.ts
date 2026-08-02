export type ConnectionState = "connected" | "unavailable" | "unsupported"

export interface TaskPaneStatus {
  state: ConnectionState
  title: string
  detail: string
}
