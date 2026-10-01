"""Interactive CLI Interface for LeadPulse."""

import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from lead_pulse.pipeline import LeadPipeline
from lead_pulse.validator import EmailValidator

console = Console()

BANNER = r"""[bold cyan]
  _                     _ _____       _          
 | |                   | |  __ \     | |         
 | |     ___  __ _   __| | |__) |   _| |___  ___ 
 | |    / _ \/ _` | / _` |  ___/ | | | / __|/ _ \
 | |___|  __/ (_| || (_| | |   | |_| | \__ \  __/
 |______\___|\__,_| \__,_|_|    \__,_|_|___/\___|
[/bold cyan]
[dim]Automated B2B Lead Extraction, Enrichment & MX Verification Engine[/dim]
[green]Developed by Abdulrazaq Adeyemi | Production Lead Engine[/green]
"""

DEMO_TARGETS = [
    "stripe.com",
    "github.com",
    "vercel.com",
    "supabase.com",
    "anthropic.com"
]


def print_lead_card(lead: dict):
    """Render a clean summary panel for a single lead."""
    ver = lead.get("verification", {})
    status_color = "green" if ver.get("deliverable") else "red"

    content = f"""[bold]Company:[/bold] {lead.get('company_name', 'N/A')}
[bold]Website:[/bold] {lead.get('url')}
[bold]Emails Found:[/bold] {', '.join(lead.get('emails', [])) or '[dim]None found[/dim]'}
[bold]Primary Email Status:[/bold] [{status_color}]{ver.get('status')} (Deliverable: {ver.get('deliverable')})[/{status_color}]
[bold]Mail Server (MX):[/bold] {ver.get('mx_server') or '[dim]None[/dim]'}
[bold]Phone Numbers:[/bold] {', '.join(lead.get('phones', [])) or '[dim]None found[/dim]'}
[bold]Social Links:[/bold] {', '.join([f'{k}: {v}' for k, v in lead.get('socials', {}).items()]) or '[dim]None[/dim]'}
[bold]Description:[/bold] [italic]{lead.get('description', '')[:120]}...[/italic]"""

    console.print(Panel(content, title=f"[cyan]{lead.get('domain')}[/cyan]", expand=False))


def cmd_scan(url: str):
    """Scan a single target."""
    console.print(BANNER)
    console.print(f"\n[bold yellow]Targeting:[/bold yellow] {url}")
    console.print("[dim]Crawling subpages and extracting contacts...[/dim]")
    pipeline = LeadPipeline()
    lead = pipeline.process_single_target(url)
    print_lead_card(lead)


def cmd_verify(email: str):
    """Verify a single email."""
    console.print(BANNER)
    console.print(f"\n[bold yellow]Verifying Email:[/bold yellow] {email}")
    console.print("[dim]Querying DNS MX records...[/dim]")
    res = EmailValidator.verify(email)

    status_color = "green" if res["deliverable"] else "red"
    console.print(Panel(
        f"[bold]Email:[/bold] {res['email']}\n"
        f"[bold]Status:[/bold] [{status_color}]{res['status']}[/{status_color}]\n"
        f"[bold]Deliverable:[/bold] [{status_color}]{res['deliverable']}[/{status_color}]\n"
        f"[bold]Mail Exchange (MX):[/bold] {res['mx_server'] or 'None'}\n"
        f"[bold]Details:[/bold] {res['reason']}\n"
        f"[bold]Generic Role Address:[/bold] {res['is_generic']}",
        title="[cyan]Deliverability Audit[/cyan]",
        expand=False
    ))


def cmd_demo():
    """Run an automated batch demo on sample target domains."""
    console.print(BANNER)
    console.print(f"\n[bold yellow]Starting Demo Scan on {len(DEMO_TARGETS)} Target Domains...[/bold yellow]\n")

    pipeline = LeadPipeline()
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Processing targets...", total=len(DEMO_TARGETS))

        def on_prog(lead):
            results.append(lead)
            progress.advance(task)

        res = pipeline.run(DEMO_TARGETS, output_prefix="demo_leads", on_progress=on_prog)

    # Render Results Table
    table = Table(title="[bold green]Enriched B2B Lead Results[/bold green]")
    table.add_column("Company", style="cyan", no_wrap=True)
    table.add_column("Domain", style="magenta")
    table.add_column("Email", style="bold")
    table.add_column("Status", style="yellow")
    table.add_column("MX Server", style="dim")
    table.add_column("Socials", style="blue")

    for r in res["records"]:
        ver = r.get("verification", {})
        emails = r.get("emails", [])
        primary_email = emails[0] if emails else "[dim]N/A[/dim]"
        social_count = len(r.get("socials", {}))

        table.add_row(
            r.get("company_name", "")[:20],
            r.get("domain", ""),
            primary_email,
            f"[{'green' if ver.get('deliverable') else 'red'}]{ver.get('status')}[/]",
            ver.get("mx_server") or "-",
            f"{social_count} profiles" if social_count else "-"
        )

    console.print(table)
    console.print(f"\n[bold green][+] Exported to CSV:[/bold green] {res['csv_path']}")
    console.print(f"[bold green][+] Exported to JSON:[/bold green] {res['json_path']}\n")


def main():
    parser = argparse.ArgumentParser(description="LeadPulse - B2B Lead Extraction & Enrichment Engine")
    subparsers = parser.add_subparsers(dest="command")

    # scan command
    p_scan = subparsers.add_parser("scan", help="Scan a single target website")
    p_scan.add_argument("url", help="Target URL (e.g. stripe.com)")

    # verify command
    p_ver = subparsers.add_parser("verify", help="Verify single email deliverability")
    p_ver.add_argument("email", help="Target email address")

    # demo command
    subparsers.add_parser("demo", help="Run automated demonstration on sample companies")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args.url)
    elif args.command == "verify":
        cmd_verify(args.email)
    elif args.command == "demo" or not args.command:
        cmd_demo()


if __name__ == "__main__":
    main()
