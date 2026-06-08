import src.app as core
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(core.start_bot())
    except KeyboardInterrupt:
        print("Бот остановлен")