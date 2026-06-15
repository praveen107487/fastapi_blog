from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )
    database_url: str
    
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    reset_token_expire_minutes: int = 60
    
    frontend_url: str = "http://127.0.0.1:8000"
    
    # Mailtrap Configuration properties
    mail_server: str = "sandbox.smtp.mailtrap.io" 
    mail_port: int = 2525                      
    mail_username: str = "260f67bda2397e"
    mail_password: SecretStr = SecretStr("d1e3ea5325b137")
    mail_form: str = "noreply@gmail.com"
    
    mail_use_tls: bool = True 

settings = Settings()