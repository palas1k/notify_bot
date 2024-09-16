from src.main import app


def main():
    bot, dp = app()
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
