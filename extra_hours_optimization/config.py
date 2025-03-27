import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = "../config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"El archivo de configuración {self.config_path} no existe")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @property
    def month(self) -> int:
        return self.config['general']['month']
    
    @property
    def year(self) -> int:
        return self.config['general']['year']
    
    @property
    def country(self) -> str:
        return self.config['general']['country']
    
    @property
    def holidays_availability(self) -> Dict[str, bool]:
        return {
            store: data['holidays_available']
            for store, data in self.config['stores'].items()
        }
    
    @property
    def maintenance_days(self) -> Dict[str, list]:
        return {
            store: data['maintenance_days']
            for store, data in self.config['stores'].items()
        }
    
    @property
    def hours_per_day(self) -> float:
        return self.config['schedule']['hours_per_day']
    
    @property
    def max_monthly_hours(self) -> int:
        return self.config['schedule']['max_monthly_hours']
    
    @property
    def max_overtime_hours(self) -> int:
        return self.config['schedule']['max_overtime_hours'] 