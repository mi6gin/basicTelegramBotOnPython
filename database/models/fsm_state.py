from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.engine import Base


class FSMStateModel(Base):
    """
    Модель для хранения FSM-состояний и данных пользователей в базе данных.
    Это позволяет состояниям полностью сохраняться при перезапуске бота.
    """
    __tablename__ = "fsm_states"

    # Ключ состояния в формате "bot_id:chat_id:user_id"
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Имя текущего состояния (например, "SupportStates:waiting_for_message")
    state: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # JSON-строка с временными данными состояния (данные FSM)
    data: Mapped[str] = mapped_column(Text, default="{}")
