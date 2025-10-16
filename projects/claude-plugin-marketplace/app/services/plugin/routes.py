"""Routes for plugin management."""
import tempfile
import shutil
from pathlib import Path
from fastapi import APIRouter, Request, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.services.auth.dependencies import require_auth
from app.services.auth.models import User
from app.services.plugin.models import Plugin, PluginVersion
from app.services.plugin.validation import validate_plugin_zip, ValidationError
from app.services.plugin.storage import (
    store_plugin_zip,
    extract_plugin_metadata,
    get_plugin_directory
)
from app.services.plugin.utils import render_markdown


router = APIRouter(prefix="/plugins", tags=["plugins"])
templates = Jinja2Templates(directory=["app/services/plugin/templates", "app/shared/templates"])


@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request, user: User = Depends(require_auth)):
    """Display the plugin upload form."""
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@router.post("/upload")
async def upload_plugin(
    request: Request,
    file: UploadFile = File(...),
    plugin_name: str = Form(""),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Handle plugin upload.
    
    Steps:
    1. Save uploaded file to temp location
    2. Validate plugin structure
    3. Check for duplicate plugin name
    4. Create or update Plugin and PluginVersion records
    5. Store files permanently
    6. Redirect to plugin detail page
    """
    temp_dir = None
    
    try:
        # Create temp directory for uploaded file
        temp_dir = Path(tempfile.mkdtemp())
        temp_zip_path = temp_dir / file.filename
        
        # Save uploaded file
        with open(temp_zip_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Validate plugin structure
        try:
            plugin_json = validate_plugin_zip(temp_zip_path)
        except ValidationError as e:
            return templates.TemplateResponse(
                "upload.html",
                {
                    "request": request,
                    "user": user,
                    "error": str(e)
                },
                status_code=400
            )
        
        # Get plugin name (from form or from plugin.json)
        name = plugin_name.strip() if plugin_name.strip() else plugin_json.get("name")
        display_name = plugin_json.get("displayName", name)
        description = plugin_json.get("description")
        version = plugin_json.get("version")
        
        # Check if plugin already exists
        existing_plugin = db.query(Plugin).filter(
            Plugin.author_id == user.id,
            Plugin.name == name
        ).first()
        
        if existing_plugin:
            # Updating existing plugin - check version
            latest_version = db.query(PluginVersion).filter(
                PluginVersion.plugin_id == existing_plugin.id,
                PluginVersion.is_latest == True
            ).first()
            
            if latest_version:
                # Compare versions
                if not is_version_higher(version, latest_version.version):
                    return templates.TemplateResponse(
                        "upload.html",
                        {
                            "request": request,
                            "user": user,
                            "error": f"Version {version} must be higher than current version {latest_version.version}"
                        },
                        status_code=400
                    )
                
                # Update is_latest flag on old version
                latest_version.is_latest = False
            
            plugin = existing_plugin
            # Update timestamp
            from datetime import datetime, UTC
            plugin.updated_at = datetime.now(UTC)
        else:
            # Create new plugin
            plugin = Plugin(
                name=name,
                display_name=display_name,
                description=description,
                author_id=user.id,
                is_published=True
            )
            db.add(plugin)
            db.commit()
            db.refresh(plugin)
        
        # Store the zip file permanently
        stored_zip_path = store_plugin_zip(
            temp_zip_path,
            user.username,
            plugin.name,
            version
        )
        
        # Extract metadata
        metadata_result = extract_plugin_metadata(
            temp_zip_path,
            user.username,
            plugin.name,
            version
        )
        
        # Create PluginVersion record
        plugin_version = PluginVersion(
            plugin_id=plugin.id,
            version=version,
            file_path=str(stored_zip_path),
            readme_content=metadata_result.get("readme_content"),
            plugin_metadata=metadata_result.get("plugin_json", {}),
            is_latest=True
        )
        db.add(plugin_version)
        db.commit()
        
        # Redirect to plugin detail page (we'll implement this in phase 3)
        # For now, redirect to homepage with success message
        return RedirectResponse(
            f"/?upload_success=1",
            status_code=303
        )
        
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Upload error: {e}")
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "user": user,
                "error": f"An error occurred during upload: {str(e)}"
            },
            status_code=500
        )
    finally:
        # Clean up temp directory
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)


@router.get("/my-plugins", response_class=HTMLResponse)
async def my_plugins(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Display list of all plugins owned by authenticated user."""
    plugins = db.query(Plugin).filter(Plugin.author_id == user.id).all()
    
    # Get latest version for each plugin
    plugin_data = []
    for plugin in plugins:
        latest = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.is_latest == True
        ).first()
        plugin_data.append({
            "plugin": plugin,
            "latest_version": latest
        })
    
    return templates.TemplateResponse("my_plugins.html", {
        "request": request,
        "user": user,
        "plugin_data": plugin_data
    })


@router.get("/@{username}/{plugin_name}", response_class=HTMLResponse)
async def plugin_detail(
    username: str,
    plugin_name: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Display detailed plugin information page."""
    # Find plugin by username and name
    author = db.query(User).filter(User.username == username).first()
    if not author:
        raise HTTPException(404, "User not found")
    
    plugin = db.query(Plugin).filter(
        Plugin.author_id == author.id,
        Plugin.name == plugin_name
    ).first()
    if not plugin or not plugin.is_published:
        raise HTTPException(404, "Plugin not found")
    
    # Get all versions, sorted newest first
    versions = db.query(PluginVersion).filter(
        PluginVersion.plugin_id == plugin.id
    ).order_by(PluginVersion.uploaded_at.desc()).all()
    
    latest = next((v for v in versions if v.is_latest), None)
    
    # Extract component counts from metadata
    components = latest.plugin_metadata.get("components", {}) if latest else {}
    
    # Render README
    readme_html = render_markdown(latest.readme_content) if latest else None
    
    # Build installation commands
    base_url = str(request.base_url).rstrip('/')
    marketplace_command = f"/plugin marketplace add {base_url}/marketplace.json"
    install_command = f"/plugin install {username}-{plugin_name}"
    
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "plugin": plugin,
        "author": author,
        "latest_version": latest,
        "versions": versions,
        "components": components,
        "readme_html": readme_html,
        "marketplace_command": marketplace_command,
        "install_command": install_command,
        "download_url": f"/plugins/@{username}/{plugin_name}/download/{latest.version}" if latest else None
    })


def is_version_higher(new_version: str, old_version: str) -> bool:
    """
    Compare two semantic versions.
    
    Args:
        new_version: New version string (e.g., "1.0.1")
        old_version: Old version string (e.g., "1.0.0")
        
    Returns:
        True if new_version > old_version
    """
    def parse_version(v: str) -> tuple:
        return tuple(int(x) for x in v.split('.'))
    
    try:
        return parse_version(new_version) > parse_version(old_version)
    except (ValueError, AttributeError):
        return False

