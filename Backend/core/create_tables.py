import boto3, os
from dotenv import load_dotenv
load_dotenv()

def create_tables():
    dynamodb = boto3.client("dynamodb",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    tables = dynamodb.list_tables()["TableNames"]
    if "Schemes" not in tables:
        dynamodb.create_table(
            TableName="Schemes",
            KeySchema=[{"AttributeName": "scheme_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "scheme_id", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
                {"AttributeName": "state", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[{
                "IndexName": "category-state-index",
                "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"},{"AttributeName": "state", "KeyType": "RANGE"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            }],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print("Schemes table created.")
    else:
        print("Schemes table already exists.")
    if "UserQueries" not in tables:
        dynamodb.create_table(
            TableName="UserQueries",
            KeySchema=[{"AttributeName": "query_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "query_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print("UserQueries table created.")
    else:
        print("UserQueries table already exists.")
    if "Users" not in tables:
        dynamodb.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print("Users table created.")
    else:
        print("Users table already exists.")
    if "Applications" not in tables:
        dynamodb.create_table(
            TableName="Applications",
            KeySchema=[{"AttributeName": "application_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "application_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print("Applications table created.")
    else:
        print("Applications table already exists.")

if __name__ == "__main__":
    create_tables()
