export interface OfficeReadyInfo {
  host: string | null
  platform: string | null
}

export interface OfficeRuntime {
  onReady(): Promise<OfficeReadyInfo>
  isWord(host: string | null): boolean
  isDesktop(platform: string | null): boolean
  supportsWordApi13(): boolean
}

export class OfficeJsRuntime implements OfficeRuntime {
  public constructor(private readonly office: typeof Office) {}

  public async onReady(): Promise<OfficeReadyInfo> {
    const info = await this.office.onReady()
    return {
      host: info.host === null ? null : String(info.host),
      platform: info.platform === null ? null : String(info.platform),
    }
  }

  public isWord(host: string | null): boolean {
    return host === String(this.office.HostType.Word)
  }

  public isDesktop(platform: string | null): boolean {
    return (
      platform === String(this.office.PlatformType.PC) ||
      platform === String(this.office.PlatformType.Mac)
    )
  }

  public supportsWordApi13(): boolean {
    return this.office.context.requirements.isSetSupported("WordApi", "1.3")
  }
}
