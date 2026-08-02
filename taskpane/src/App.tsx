import type { TaskPaneStatus } from "./status"
import "./styles.css"

interface AppProps {
  status: TaskPaneStatus
}

export function App({ status }: AppProps): React.JSX.Element {
  return (
    <section className={`status status--${status.state}`} data-status={status.state}>
      <p className="eyebrow">Word Researcher · Phase 1</p>
      <h1>{status.title}</h1>
      <p>{status.detail}</p>
    </section>
  )
}
