from match_scheduler.match_scheduler import main, setup_logging

if __name__ == "__main__":
    LOGGER = setup_logging()
    try:
        main()
    except Exception as err:
        # make sure it gets logged
        LOGGER.exception(err)
        raise err
