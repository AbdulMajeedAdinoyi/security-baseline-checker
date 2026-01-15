import platform

class PlatformDetector:
    def __init__(self):
        self.os_type = None
    
    def detect_platform(self):
        """Detect the operating system"""
        system = platform.system()
        
        if system == "Windows":
            self.os_type = "Windows"
            return "Windows"
        elif system == "Linux":
            self.os_type = "Linux"
            return "Linux"
        else:
            return None
    
    def get_os_details(self):
        """Get detailed OS information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine()
        }