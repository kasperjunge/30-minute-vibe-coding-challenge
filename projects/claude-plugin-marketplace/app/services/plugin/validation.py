"""Plugin validation logic for validating uploaded plugins."""
import zipfile
import json
import re
from pathlib import Path
from typing import Dict


class ValidationError(Exception):
    """Custom exception for validation errors with user-friendly messages."""
    pass


def validate_plugin_zip(zip_path: Path) -> Dict:
    """
    Validate plugin zip structure and return metadata.
    
    Args:
        zip_path: Path to the plugin zip file
        
    Returns:
        Dict containing plugin.json contents and metadata
        
    Raises:
        ValidationError: If validation fails with user-friendly message
    """
    # Check if zip is valid
    if not zipfile.is_zipfile(zip_path):
        raise ValidationError("Uploaded file is not a valid ZIP file.")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Check for forbidden files first
            check_forbidden_files(zf)
            
            # Find .claude-plugin/plugin.json - it might be at root or in a subdirectory
            plugin_json_path = None
            for name in zf.namelist():
                if name.endswith('.claude-plugin/plugin.json'):
                    plugin_json_path = name
                    break
            
            if not plugin_json_path:
                raise ValidationError(
                    "Plugin must contain .claude-plugin/plugin.json file. "
                    "Please ensure your plugin follows the Claude Code plugin structure."
                )
            
            # Read and parse JSON
            try:
                plugin_json_content = zf.read(plugin_json_path).decode('utf-8')
                plugin_json = json.loads(plugin_json_content)
            except json.JSONDecodeError as e:
                raise ValidationError(
                    f"Invalid JSON in .claude-plugin/plugin.json: {str(e)}. "
                    "Please check your plugin.json syntax."
                )
            except UnicodeDecodeError:
                raise ValidationError(
                    ".claude-plugin/plugin.json must be UTF-8 encoded text file."
                )
            
            # Validate required fields
            required_fields = ["name", "version", "description"]
            missing_fields = [field for field in required_fields if field not in plugin_json]
            
            if missing_fields:
                raise ValidationError(
                    f"Missing required fields in plugin.json: {', '.join(missing_fields)}. "
                    "A valid plugin.json must include: name, version, and description."
                )
            
            # Validate version format
            version = plugin_json.get("version", "")
            if not validate_version_format(version):
                raise ValidationError(
                    f"Invalid version format '{version}'. "
                    "Version must follow semantic versioning (e.g., 1.0.0, 2.1.3)."
                )
            
            # Extract name and validate it
            name = plugin_json.get("name", "")
            if not name or not isinstance(name, str):
                raise ValidationError("Plugin name must be a non-empty string.")
            
            # Validate description
            description = plugin_json.get("description", "")
            if not description or not isinstance(description, str):
                raise ValidationError("Plugin description must be a non-empty string.")
            
            return plugin_json
            
    except zipfile.BadZipFile:
        raise ValidationError("Uploaded file is corrupted or not a valid ZIP file.")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error validating plugin: {str(e)}")


def validate_version_format(version: str) -> bool:
    """
    Check if version follows semantic versioning (x.y.z).
    
    Args:
        version: Version string to validate
        
    Returns:
        True if version is valid semver, False otherwise
    """
    if not isinstance(version, str):
        return False
    
    # Semantic versioning pattern: major.minor.patch
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def check_forbidden_files(zip_file: zipfile.ZipFile) -> None:
    """
    Check for executable or forbidden file types in the zip.
    
    Args:
        zip_file: ZipFile object to check
        
    Raises:
        ValidationError: If forbidden files are found
    """
    forbidden_extensions = {'.exe', '.sh', '.bat', '.cmd', '.dll', '.so', '.dylib'}
    
    for file_info in zip_file.filelist:
        # Skip directories
        if file_info.is_dir():
            continue
        
        file_path = Path(file_info.filename)
        file_ext = file_path.suffix.lower()
        
        if file_ext in forbidden_extensions:
            raise ValidationError(
                f"Forbidden file type detected: {file_info.filename}. "
                f"Executable files ({', '.join(forbidden_extensions)}) are not allowed for security reasons."
            )

