import os
import yaml
import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import tempfile

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from server import PromptServer


class YAMLFileHandler(FileSystemEventHandler):
    """Handles file system events for YAML files"""
    def __init__(self, node_instance):
        self.node_instance = node_instance
        
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            self.node_instance.refresh_enums()
    
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            self.node_instance.refresh_enums()
    
    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            self.node_instance.refresh_enums()


class NS_PromptList:
    """NS-PromptList Node for ComfyUI"""
    
    def __init__(self):
        self.yaml_dir = Path(__file__).parent / "yaml"
        self.yaml_dir.mkdir(exist_ok=True)
        
        self.write_lock = asyncio.Lock()
        self.observer = None
        self.file_handler = YAMLFileHandler(self)
        
        # Store server instance
        self.server = PromptServer.instance
        
        # Start watchdog observer
        self._start_watchdog()
        
        # Register socket handlers
        self._register_socket_handlers()
        
        # Initial enum refresh
        self.refresh_enums()
    
    @classmethod
    def INPUT_TYPES(cls):
        # Always get fresh YAML list when INPUT_TYPES is called
        yaml_dir = Path(__file__).parent / "yaml"
        yaml_dir.mkdir(exist_ok=True)
        
        yaml_files = [f.name for f in yaml_dir.glob("*.yaml")]
        if not yaml_files:
            # Create default yaml if none exist
            default_yaml = yaml_dir / "default.yaml"
            default_yaml.write_text("example:\n  prompt: 'Enter your prompt here'\n")
            yaml_files = ["default.yaml"]
        
        # Get all possible titles from all YAML files for validation
        all_titles = set([""])  # Always include empty string
        for yaml_file in yaml_files:
            yaml_path = yaml_dir / yaml_file
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    all_titles.update(data.keys())
            except:
                pass
        
        return {
            "required": {
                "select_yaml": (sorted(yaml_files), {"default": yaml_files[0] if yaml_files else ""}),
                "select": (sorted(list(all_titles)), {"default": ""}),  # Include all possible titles
                "title": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "NS"
    
    @classmethod
    def _get_instance(cls):
        """Get or create singleton instance"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    def _get_yaml_files(self) -> List[str]:
        """Get list of YAML files in yaml directory"""
        if not self.yaml_dir.exists():
            return ["default.yaml"]
        
        yaml_files = [f.name for f in self.yaml_dir.glob("*.yaml")]
        if not yaml_files:
            # Create default yaml if none exist
            default_yaml = self.yaml_dir / "default.yaml"
            default_yaml.write_text("example:\n  prompt: 'Enter your prompt here'\n")
            yaml_files = ["default.yaml"]
        
        return sorted(yaml_files)
    
    def _get_titles_from_yaml(self, yaml_file: str) -> List[str]:
        """Get titles from a YAML file"""
        yaml_path = self.yaml_dir / yaml_file
        if not yaml_path.exists():
            return [""]
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return list(data.keys())
        except Exception as e:
            print(f"Error reading YAML {yaml_file}: {e}")
            self._handle_corrupt_yaml(yaml_path)
            return [""]
    
    def _handle_corrupt_yaml(self, yaml_path: Path):
        """Handle corrupt YAML by renaming and creating new"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bad_path = yaml_path.parent / f"bad_{timestamp}_{yaml_path.name}"
        shutil.move(str(yaml_path), str(bad_path))
        yaml_path.write_text("# Recovered from corrupt file\n")
    
    def _start_watchdog(self):
        """Start file system observer"""
        if self.observer is None:
            self.observer = Observer()
            self.observer.schedule(self.file_handler, str(self.yaml_dir), recursive=False)
            self.observer.start()
    
    def refresh_enums(self):
        """Refresh YAML and title enums, broadcast update"""
        yaml_files = self._get_yaml_files()
        
        # Build enum data for all YAML files
        enum_data = {
            "yaml_files": yaml_files,
            "titles_by_yaml": {}
        }
        
        for yaml_file in yaml_files:
            titles = self._get_titles_from_yaml(yaml_file)
            enum_data["titles_by_yaml"][yaml_file] = titles
        
        self._broadcast_enum(enum_data)
    
    def _broadcast_enum(self, enum_data: Dict):
        """Broadcast enum update to frontend"""
        if hasattr(self.server, 'send_sync'):
            self.server.send_sync("ns_promptlist_enum", enum_data)
        else:
            # Alternative method for older ComfyUI versions
            try:
                from aiohttp import web
                if hasattr(self.server, 'socketio'):
                    self.server.socketio.emit("ns_promptlist_enum", enum_data)
            except:
                pass
    
    def _register_socket_handlers(self):
        """Register socket.io handlers"""
        server = PromptServer.instance
        
        @server.routes.post("/ns_promptlist/get_prompt")
        async def get_prompt(request):
            data = await request.json()
            yaml_file = data.get("yaml", "")
            title = data.get("title", "")
            
            response_data = self._get_prompt_data(yaml_file, title)
            
            # Send via websocket
            if hasattr(server, 'send_sync'):
                server.send_sync("ns_promptlist_set_widgets", response_data)
            
            return {"success": True}
        
        @server.routes.post("/ns_promptlist/reload_yamls")
        async def reload_yamls(request):
            """Force reload YAML list"""
            self.refresh_enums()
            return {"success": True}
    
    def _get_prompt_data(self, yaml_file: str, title: str) -> Dict[str, str]:
        """Get prompt data from YAML"""
        yaml_path = self.yaml_dir / yaml_file
        
        if not yaml_path.exists():
            return {"title": title, "prompt": ""}
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            if title in data and isinstance(data[title], dict):
                prompt = data[title].get("prompt", "")
            else:
                prompt = ""
            
            return {"title": title, "prompt": prompt}
        except Exception as e:
            print(f"Error reading prompt: {e}")
            return {"title": title, "prompt": ""}
    
    async def _save_yaml(self, yaml_file: str, data: Dict):
        """Atomic save YAML with lock"""
        async with self.write_lock:
            yaml_path = self.yaml_dir / yaml_file
            
            # Use temporary file for atomic write
            with tempfile.NamedTemporaryFile(mode='w', dir=str(self.yaml_dir), 
                                           delete=False, encoding='utf-8') as tmp:
                yaml.dump(data, tmp, default_flow_style=False, allow_unicode=True, 
                         sort_keys=True)
                tmp_path = tmp.name
            
            # Atomic replace
            os.replace(tmp_path, str(yaml_path))
    
    def delete_title(self, yaml_file: str, title: str):
        """Delete a title from YAML"""
        yaml_path = self.yaml_dir / yaml_file
        
        if not yaml_path.exists():
            return
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            if title in data:
                del data[title]
                # Run async save in sync context
                asyncio.run(self._save_yaml(yaml_file, data))
                self.refresh_enums()
        except Exception as e:
            print(f"Error deleting title: {e}")
    
    def run(self, select_yaml: str, select: str, title: str, prompt: str, 
            unique_id: str) -> Tuple[str]:
        """Main execution function"""
        
        # Check prompt length warning
        if len(prompt) > 4096:
            print(f"Warning: Prompt length ({len(prompt)} chars) exceeds recommended 4096 chars")
        
        # Save current prompt to YAML
        if title and prompt:
            yaml_path = self.yaml_dir / select_yaml
            
            try:
                # Read existing data
                if yaml_path.exists():
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f) or {}
                else:
                    data = {}
                
                # Update or create entry
                if title not in data:
                    data[title] = {}
                data[title]["prompt"] = prompt
                
                # Save
                asyncio.run(self._save_yaml(select_yaml, data))
                
            except Exception as e:
                print(f"Error saving prompt: {e}")
        
        return (prompt,)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """Force re-execution on each run"""
        # This ensures the node re-validates inputs each time
        return float("NaN")
    
    @classmethod
    def VALIDATE_INPUTS(cls, select_yaml, select, title, prompt, unique_id):
        """Validate inputs - always return True to avoid validation errors"""
        # Since we're dynamically updating the select options,
        # we need to bypass ComfyUI's static validation
        return True


# Singleton instance
_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = NS_PromptList()
    return _instance


NODE_CLASS_MAPPINGS = {
    "NS-PromptList": NS_PromptList
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NS-PromptList": "NS Prompt List"
}

# Initialize instance on import
get_instance()