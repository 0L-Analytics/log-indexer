
class BaseConfig:
    DEBUG=1
    PATH_VALIDATOR_LOG_FILES="/home/user/projects/log-indexer/assets/logs"


class TestConfig(BaseConfig):
    SOUND_ON_ERROR=0
    PATH_TEST_FILE="/home/user/projects/log-indexer/assets/daterange_test.txt"


class ProdConfig(BaseConfig):
    TIME_GAP_LIST=[
        ("2022-11-20T09:00:00", "2022-11-20T10:00:00"),
        ("2022-11-21T09:00:00", "2022-11-21T10:00:00"),
    ]
    INITIATE_MODEL=1
    DATABASE_URL="postgresql://research:research@localhost:5432/research"
    # SQL_HOST="researchDB"
    # SQL_PORT="5432"
    # DATABASE="research"
