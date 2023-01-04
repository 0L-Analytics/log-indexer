
class BaseConfig:
    DEBUG=1
    PATH_VALIDATOR_LOG_FILES="/home/user/projects/log-indexer/assets/logs"


class TestConfig(BaseConfig):
    SOUND_ON_ERROR=0
    PATH_TEST_FILE="/home/user/projects/log-indexer/assets/daterange_test.txt"


class ProdConfig(BaseConfig):
    TIME_GAP_LIST=[
        ("2022-11-21T23:00:00", "2022-11-22T01:55:00"),
    ]
    DATABASE_URL="postgresql://research:research@researchDB:5432/research"
    SQL_HOST="researchDB"
    SQL_PORT="5432"
    DATABASE="research"
