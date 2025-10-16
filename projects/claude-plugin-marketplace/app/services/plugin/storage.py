"""File storage logic for plugin files and metadata."""
import zipfile
import json
import shutil
from pathlib import Path
from typing import Dict, Optional


PLUGINS_DIR = Path("data/plugins")


def get_plugin_directory(username: str, plugin_name: str) -> Path:
    """
    Get or create plugin storage directory.
    
    Args:
        username: Username of the plugin author
        plugin_name: Name of the plugin
        
    Returns:
        Path to the plugin directory
    """
    plugin_dir = PLUGINS_DIR / username / plugin_name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    return plugin_dir


def store_plugin_zip(
    zip_path: Path,
    username: str,
    plugin_name: str,
    version: str
) -> Path:
    """
    Store plugin zip file in permanent location.
    
    Args:
        zip_path: Path to the uploaded zip file
        username: Username of the plugin author
        plugin_name: Name of the plugin
        version: Version string
        
    Returns:
        Path to the stored zip file
    """
    plugin_dir = get_plugin_directory(username, plugin_name)
    dest_path = plugin_dir / f"{version}.zip"
    
    # Copy the zip file
    shutil.copy(zip_path, dest_path)
    
    return dest_path


def extract_plugin_metadata(
    zip_path: Path,
    username: str,
    plugin_name: str,
    version: str
) -> Dict:
    """
    Extract plugin.json and README.md to metadata directory.
    
    Args:
        zip_path: Path to the plugin zip file
        username: Username of the plugin author
        plugin_name: Name of the plugin
        version: Version string
        
    Returns:
        Dict with extracted metadata including readme_content and plugin_json
    """
    plugin_dir = get_plugin_directory(username, plugin_name)
    metadata_dir = plugin_dir / "metadata" / version
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    plugin_json = None
    readme_content = None
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Find plugin.json - it might be at root or in a subdirectory
        plugin_json_path = None
        for name in zf.namelist():
            if name.endswith('.claude-plugin/plugin.json'):
                plugin_json_path = name
                break
        
        # Extract plugin.json
        if plugin_json_path:
            plugin_json_content = zf.read(plugin_json_path).decode('utf-8')
            plugin_json = json.loads(plugin_json_content)
            
            # Write to metadata directory
            with open(metadata_dir / "plugin.json", 'w') as f:
                json.dump(plugin_json, f, indent=2)
        
        # Extract README.md if present (handle both root and subdirectory)
        readme_files = [name for name in zf.namelist() 
                       if name.endswith('README.md') or name.endswith('Readme.md') or name.endswith('readme.md')]
        if readme_files:
            readme_content = zf.read(readme_files[0]).decode('utf-8', errors='replace')
            
            # Write to metadata directory
            with open(metadata_dir / "README.md", 'w') as f:
                f.write(readme_content)
        
        # Count components
        components = count_components(zf)
    
    return {
        "plugin_json": plugin_json,
        "readme_content": readme_content,
        "components": components
    }


def count_components(zip_file: zipfile.ZipFile) -> Dict[str, int]:
    """
    Count files in each component directory within the zip.
    Handles both root-level and subdirectory structures.
    
    Args:
        zip_file: ZipFile object
        
    Returns:
        Dict with component counts
    """
    component_dirs = ["commands/", "agents/", "skills/", "hooks/", "mcp_servers/"]
    counts = {}
    
    for component_dir in component_dirs:
        count = 0
        for name in zip_file.namelist():
            # Skip directories
            if name.endswith('/'):
                continue
            
            # Check if this file is in the component directory
            # Handle both "commands/" and "plugin-name/commands/"
            parts = name.split('/')
            
            # Find the component directory in the path
            if component_dir.rstrip('/') in parts:
                idx = parts.index(component_dir.rstrip('/'))
                # Check if it's a direct child (only one level deep)
                if idx < len(parts) - 2:  # Has nested subdirectories
                    # For skills, we want to count SKILL.md files
                    if component_dir == "skills/" and parts[-1] == "SKILL.md":
                        count += 1
                elif idx == len(parts) - 2:  # Direct child file
                    count += 1
        
        # Remove trailing slash for key name
        component_name = component_dir.rstrip('/')
        counts[component_name] = count
    
    return counts


def delete_plugin_files(username: str, plugin_name: str) -> None:
    """
    Delete all files for a plugin (when unpublished).
    
    Args:
        username: Username of the plugin author
        plugin_name: Name of the plugin
    """
    plugin_dir = PLUGINS_DIR / username / plugin_name
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)


def get_plugin_zip_path(username: str, plugin_name: str, version: str) -> Optional[Path]:
    """
    Get the path to a plugin zip file.
    
    Args:
        username: Username of the plugin author
        plugin_name: Name of the plugin
        version: Version string
        
    Returns:
        Path to the zip file if it exists, None otherwise
    """
    plugin_dir = PLUGINS_DIR / username / plugin_name
    zip_path = plugin_dir / f"{version}.zip"
    
    return zip_path if zip_path.exists() else None

