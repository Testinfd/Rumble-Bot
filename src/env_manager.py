"""
Environment Configuration Manager for Rumble Bot
Handles secure environment variable management through Telegram commands
"""

import os
import re
from typing import Dict, Optional, Tuple, List
from .logger import log
from .security import credential_manager


class EnvironmentManager:
    """Manages environment variables securely through Telegram interface"""
    
    def __init__(self):
        self.env_file_path = ".env"
        
        # Define configurable environment variables
        self.configurable_vars = {
            'RUMBLE_EMAIL': {
                'description': 'Rumble account email',
                'type': 'email',
                'sensitive': True,
                'required': True
            },
            'RUMBLE_PASSWORD': {
                'description': 'Rumble account password',
                'type': 'password',
                'sensitive': True,
                'required': True
            },
            'RUMBLE_CHANNEL': {
                'description': 'Default Rumble channel name',
                'type': 'text',
                'sensitive': False,
                'required': True
            },
            'MAX_FILE_SIZE_MB': {
                'description': 'Maximum file size in MB',
                'type': 'number',
                'sensitive': False,
                'required': False,
                'default': '2048'
            },
            'UPLOAD_TIMEOUT_SECONDS': {
                'description': 'Upload timeout in seconds',
                'type': 'number',
                'sensitive': False,
                'required': False,
                'default': '3600'
            },
            'RETRY_ATTEMPTS': {
                'description': 'Number of retry attempts',
                'type': 'number',
                'sensitive': False,
                'required': False,
                'default': '3'
            },
            'HEADLESS_MODE': {
                'description': 'Run browser in headless mode',
                'type': 'boolean',
                'sensitive': False,
                'required': False,
                'default': 'true'
            },
            'LOG_LEVEL': {
                'description': 'Logging level (DEBUG, INFO, WARNING, ERROR)',
                'type': 'choice',
                'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                'sensitive': False,
                'required': False,
                'default': 'INFO'
            }
        }
        
        log.info("EnvironmentManager initialized")
    
    def get_configuration_status(self) -> Dict[str, any]:
        """Get current configuration status"""
        status = {
            'configured': {},
            'missing': [],
            'total_vars': len(self.configurable_vars),
            'configured_count': 0
        }
        
        for var_name, var_config in self.configurable_vars.items():
            current_value = os.getenv(var_name)
            
            if current_value:
                status['configured'][var_name] = {
                    'description': var_config['description'],
                    'type': var_config['type'],
                    'sensitive': var_config['sensitive'],
                    'value': '***HIDDEN***' if var_config['sensitive'] else current_value
                }
                status['configured_count'] += 1
            else:
                if var_config['required']:
                    status['missing'].append({
                        'name': var_name,
                        'description': var_config['description'],
                        'type': var_config['type'],
                        'required': True
                    })
        
        return status
    
    def validate_value(self, var_name: str, value: str) -> Tuple[bool, str]:
        """Validate environment variable value"""
        if var_name not in self.configurable_vars:
            return False, f"Unknown variable: {var_name}"
        
        var_config = self.configurable_vars[var_name]
        
        # Type validation
        if var_config['type'] == 'email':
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                return False, "Invalid email format"
        
        elif var_config['type'] == 'number':
            try:
                num_value = int(value)
                if num_value <= 0:
                    return False, "Number must be positive"
            except ValueError:
                return False, "Must be a valid number"
        
        elif var_config['type'] == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                return False, "Must be true/false, yes/no, or 1/0"
        
        elif var_config['type'] == 'choice':
            if value.upper() not in var_config['choices']:
                return False, f"Must be one of: {', '.join(var_config['choices'])}"
        
        elif var_config['type'] == 'password':
            if len(value) < 6:
                return False, "Password must be at least 6 characters"
        
        elif var_config['type'] == 'text':
            if len(value.strip()) == 0:
                return False, "Value cannot be empty"
        
        return True, "Valid"
    
    def set_environment_variable(self, var_name: str, value: str) -> Tuple[bool, str]:
        """Set environment variable securely"""
        try:
            # Validate the variable
            is_valid, validation_msg = self.validate_value(var_name, value)
            if not is_valid:
                return False, validation_msg
            
            # Normalize boolean values
            if self.configurable_vars[var_name]['type'] == 'boolean':
                value = 'true' if value.lower() in ['true', '1', 'yes'] else 'false'
            
            # Normalize choice values
            elif self.configurable_vars[var_name]['type'] == 'choice':
                value = value.upper()
            
            # Set in current environment
            os.environ[var_name] = value
            
            # Update .env file
            self._update_env_file(var_name, value)
            
            log.info(f"Environment variable {var_name} updated successfully")
            return True, f"✅ {var_name} updated successfully"
            
        except Exception as e:
            log.error(f"Error setting environment variable {var_name}: {e}")
            return False, f"❌ Error updating {var_name}: {str(e)}"
    
    def _update_env_file(self, var_name: str, value: str):
        """Update .env file with new variable"""
        env_lines = []
        var_found = False
        
        # Read existing .env file if it exists
        if os.path.exists(self.env_file_path):
            with open(self.env_file_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update existing variable or add new one
        for i, line in enumerate(env_lines):
            if line.strip().startswith(f"{var_name}="):
                env_lines[i] = f"{var_name}={value}\n"
                var_found = True
                break
        
        # Add new variable if not found
        if not var_found:
            env_lines.append(f"{var_name}={value}\n")
        
        # Write back to file
        with open(self.env_file_path, 'w') as f:
            f.writelines(env_lines)
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for configuration"""
        status = self.get_configuration_status()

        if not status['missing']:
            return """✅ <b>Configuration Complete!</b>

All required environment variables are configured.
Use <code>/config status</code> to view current settings."""

        instructions = """🔧 <b>Environment Configuration Setup</b>

<b>Missing Required Variables:</b>"""

        for var in status['missing']:
            instructions += f"\n• <b>{var['name']}</b>: {var['description']}"

        instructions += """

<b>To configure a variable, use:</b>
<code>/config set VARIABLE_NAME value</code>

<b>Examples:</b>
• <code>/config set RUMBLE_EMAIL your@email.com</code>
• <code>/config set RUMBLE_PASSWORD yourpassword</code>
• <code>/config set RUMBLE_CHANNEL "Your Channel Name"</code>

<b>Available Commands:</b>
• <code>/config status</code> - View current configuration
• <code>/config list</code> - List all configurable variables
• <code>/config set VAR value</code> - Set a variable
• <code>/config help</code> - Show this help

<b>⚠️ Security Note:</b>
Sensitive data (passwords, emails) will be hidden in status displays."""

        return instructions
    
    def get_variable_list(self) -> str:
        """Get list of all configurable variables"""
        var_list = "🔧 <b>Configurable Environment Variables:</b>\n\n"

        for var_name, var_config in self.configurable_vars.items():
            required_text = "<b>Required</b>" if var_config['required'] else "Optional"
            default_text = f" (Default: {var_config.get('default', 'None')})" if 'default' in var_config else ""

            var_list += f"• <b>{var_name}</b>: {var_config['description']}\n"
            var_list += f"  Type: {var_config['type']} | {required_text}{default_text}\n\n"

        return var_list
