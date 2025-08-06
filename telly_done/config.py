from typing import Dict, Optional
import yaml
import pwd
import os
import click


def home_dir():
    uid = os.getuid()
    maybe_prev_uid = os.environ.get("SUDO_UID")
    if maybe_prev_uid is not None:
        uid = int(maybe_prev_uid)
    return pwd.getpwuid(uid).pw_dir


default_config_file_list = []
default_config_file_list.append(os.path.join(home_dir(), ".telly_done"))
default_config_file_list.append("/etc/telly_done")


def get_config(specified_path: str = None) -> Dict:
    if specified_path is not None:
        with open(specified_path, "r") as f:
            try:
                config = yaml.safe_load(f)
                return config
            except Exception:
                return {}
    else:
        for config_file in default_config_file_list:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    try:
                        config = yaml.safe_load(f)
                        return config
                    except Exception:
                        pass
        return {}


def create_config_interactively(config_path: Optional[str] = None) -> Optional[str]:
    """Interactively create a configuration file."""
    if config_path is None:
        config_path = os.path.join(home_dir(), ".telly_done")
    
    click.echo("Welcome to TellyDone configuration setup!")
    click.echo(f"Creating configuration file at: {config_path}")
    
    # Check if config file already exists
    if os.path.exists(config_path):
        if not click.confirm(f"Configuration file already exists at {config_path}. Overwrite?"):
            return config_path
    
    config = {}
    
    # Configure apprise URLs
    click.echo("\n--- Apprise Notification URLs ---")
    click.echo("Apprise supports many notification services. Examples:")
    click.echo("- Discord: discord://webhook_id/webhook_token")
    click.echo("- Slack: slack://token_a/token_b/token_c/channel")
    click.echo("- Telegram: tgram://bot_token/chat_id")
    click.echo("- Email: mailto://user:password@domain.com")
    
    apprise_urls = []
    while True:
        url = click.prompt("Enter an apprise URL (or press Enter to finish)", 
                          default="", show_default=False)
        if not url:
            break
        apprise_urls.append(url)
        click.echo(f"Added: {url}")
    
    if not apprise_urls:
        click.echo("No apprise URLs provided. Adding placeholder...")
        apprise_urls = ["# Add your apprise URLs here"]
    
    config["apprise_url"] = apprise_urls
    
    # Configure watch settings
    click.echo("\n--- Watch Settings ---")
    continuous = click.confirm("Enable continuous notifications while process is running?", 
                              default=False)
    interval = click.prompt("Notification interval in seconds", 
                           type=int, default=1800)
    include_full_process_name = click.confirm("Include full process name in finish notifications?", 
                                            default=True)
    
    config["watch"] = {
        "continuous": continuous,
        "interval": interval,
        "include_full_process_name": include_full_process_name
    }
    
    # Create directory if it doesn't exist
    config_dir = os.path.dirname(config_path)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    # Write configuration file
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        click.echo(f"\n✓ Configuration file created successfully at: {config_path}")
        
        # Display the created configuration
        click.echo("\nGenerated configuration:")
        click.echo("-" * 40)
        with open(config_path, "r") as f:
            click.echo(f.read())
        
    except Exception as e:
        click.echo(f"Error writing configuration file: {e}", err=True)
        return None
    
    return config_path
