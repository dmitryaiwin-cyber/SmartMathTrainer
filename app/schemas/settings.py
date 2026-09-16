from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    sound_enabled: bool = True
    theme: str = "light"
